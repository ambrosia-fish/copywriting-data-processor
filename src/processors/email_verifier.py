import logging
from typing import Dict, List

from email_validator import EmailNotValidError, validate_email


class EmailVerifier:
    """Verifies and cleans email addresses."""
    
    def __init__(self, config: Dict):
        """Initialize the email verifier.
        
        Args:
            config: Configuration dictionary for the email verifier
        """
        self.config = config
        self.method = config.get('method', 'basic')
    
    def process(self, newsletters: List[Dict]) -> List[Dict]:
        """Verify and clean email addresses in newsletter data.
        
        Args:
            newsletters: List of newsletter data dictionaries
        
        Returns:
            List of newsletter data dictionaries with verified emails
        """
        logging.info(f"Verifying emails for {len(newsletters)} newsletters")
        
        for newsletter in newsletters:
            email = newsletter.get('email', '')
            
            if email:
                verified_email = self._verify_email(email)
                newsletter['email'] = verified_email
        
        return newsletters
    
    def _verify_email(self, email: str) -> str:
        """Verify if an email is valid.
        
        Args:
            email: Email address to verify
        
        Returns:
            The cleaned email if valid, empty string otherwise
        """
        if not email:
            return ''
        
        try:
            # Basic validation (format and DNS)
            valid = validate_email(email)
            return valid.email
        except EmailNotValidError:
            return ''