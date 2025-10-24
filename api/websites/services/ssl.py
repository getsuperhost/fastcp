from .fcp_acme import FastcpAcme
import requests
import os
from core.utils.filesystem import get_website_paths
from core.signals import restart_services
from core.models import Domain
from django.conf import settings


# Verify path
FCP_VERIFY_PATH = '/.well-known/fastcp-verify.txt'
FCP_VERIFY_STR = 'fastcp' # This should be written to the verify file above by the installer
ACME_VERIFY_BASE_DIR = '/var/fastcp/well-known'
FCP_ACME_CONFIG_DIR = '/var/fastcp/.config'
FCP_ACCOUNT_KEY_PATH = os.path.join(FCP_ACME_CONFIG_DIR, 'account_key')
FCP_ACCOUNT_RESOURCE_PATH = os.path.join(FCP_ACME_CONFIG_DIR, 'account_resource')


class FastcpSsl(object):
    """FastCP SSL.
    
    This class deals with Let's Encrypt SSL certificates for domains.
    
    Attributes:
        regr (str): The ACME account JSON string.
        acc_key (str): The ACME account key JSON string.
    """
    regr = None
    acc_key = None
    
    def __init__(self) -> None:
        # Create if config dir not exists
        if not os.path.exists(FCP_ACME_CONFIG_DIR):
            os.makedirs(FCP_ACME_CONFIG_DIR)
        
        # Load account key and account resource
        if os.path.exists(FCP_ACCOUNT_KEY_PATH):
            with open(FCP_ACCOUNT_KEY_PATH) as f:
                self.acc_key = f.read()
        
        if os.path.exists(FCP_ACCOUNT_RESOURCE_PATH):
            with open(FCP_ACCOUNT_RESOURCE_PATH) as f:
                self.regr = f.read()
            
    
    def is_resolving(self, domain: str) -> bool:
        """Check resolving or not.
        
        This method checks and verifies either the provided domain is resolving to the
        server IP or not. If it does, the verify path above should return a 200 status
        code with fastcp as text in response.
        
        Args:
            domain (str): The domain name.
        
        Returns:
            bool: True on success Falase otherwise.
        """
        
        try:
            res = requests.get(f'https://{domain}{FCP_VERIFY_PATH}', timeout=5)
            if res.status_code == 200 and res.text.strip() == FCP_VERIFY_STR:
                return True
        except Exception:
            # We aren't interested in the reason of failure
            pass
        
        return False

    
    def get_ssl(self, website) -> bool:
        """Get SSL.
        
        This method attempts to get SSL certificates for the provided domain names. An SSL
        is requested only if the domain is found to be resolving to the server IP, otherwise
        it is excluded from the list.
        
        First of all, SSL certs are requested from Let's Encrypt. If succeeded, SSL cert files
        are generated and SSL vhost file is created.
        
        Args:
            website (object): The website model object.
        
        Returns:
            bool: True on success False otherwise.
        """
        token_paths = []
        status = False
        try:
            verified_domains = []
            
            for dom in website.domains.all():
                if self.is_resolving(dom.domain):
                    verified_domains.append(dom.domain)
                    
            
            # Get website paths
            paths = get_website_paths(website)
            if not os.path.exists(paths.get('ssl_base')):
                os.makedirs(paths.get('ssl_base'))
            
            if os.path.exists(paths.get('priv_key_path')):
                with open(paths.get('priv_key_path', 'rb')) as f:
                    priv_key = f.read()
            else:
                priv_key = None
            
            if len(verified_domains):
                acme = FastcpAcme(staging=settings.LETSENCRYPT_IS_STAGING, acc_key=self.acc_key, regr=self.regr)
                
                # Save account key
                if not self.acc_key:
                    with open(FCP_ACCOUNT_KEY_PATH, 'w') as f:
                        f.write(acme.acc_key.json_dumps())
                
                # Save account resource so we will not need to register an account
                # again and again.
                if not self.regr:
                    with open(FCP_ACCOUNT_RESOURCE_PATH, 'w') as f:
                        f.write(acme.regr.json_dumps())
                
                # Initiate an order
                results = acme.request_ssl(domains=verified_domains, priv_key=priv_key)
                
                # Write the challenge token to path
                if results:
                    base_dir = os.path.join(ACME_VERIFY_BASE_DIR, 'acme-challenge')
                    if not os.path.exists(base_dir):
                        os.makedirs(base_dir)
                    
                    for result in results:
                        token_path = os.path.join(base_dir, os.path.basename(result.get('path')))
                        token_paths.append(token_path)
                        with open(token_path, 'wb') as f:
                            f.write(result.get('token'))
                
                # After the challange token is written, request SSL cert
                result = acme.get_ssl()
                
                if result:
                    # Write private key
                    with open(paths.get('priv_key_path'), 'wb') as f:
                        try:
                            priv_key = result.get('priv_key').encode()
                        except AttributeError:
                            priv_key = result.get('priv_key')
                        
                        # Write private key
                        f.write(priv_key)
                    
                    # Write cert chain
                    with open(paths.get('cert_chain_path'), 'w') as f:
                        f.write(str(result.get('full_chain')))
                        
                    # Restart NGINX
                    restart_services.send(sender=None, services='nginx')
                    
                    # Update domains
                    for dom in verified_domains:
                        Domain.objects.filter(domain=dom).update(ssl=True)
                            
                status = True
        except Exception:
            pass
        finally:
            # Remove verification files
            if len(token_paths):
                for token_path in token_paths:
                    if token_path and os.path.exists(token_path):
                        os.remove(token_path)
        
        return status
                
