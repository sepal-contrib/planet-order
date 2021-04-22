from sepal_ui import sepalwidgets as sw 

from component import parameter as cp
from component.message import cm

class CustomPassword(sw.PasswordField):
    
    def __init__(self):
        
        self.default_key = cp.default_planet_key
        
        super().__init__(label=cm.key.password.label, v_model=self.default_key, class_ = 'mb-2')
        
        self.observe(self._check_default, 'v_model')
        
        
    def _toggle_pwd(self, widget, event, data):
        """only authorize the visibility toogle if the password is different than the default key"""
        
        # clean the error_message attribute 
        self.error_messages = None
        
        # check if the current key is the default one
        if self.default_key and self.default_key == self.v_model:
            self.error_messages = cm.key.password.error_msg
        else:
            super()._toggle_pwd(widget, event, data)
            
        return self
    
    def _check_default(self, change):
        """automatically hide the key if the user write the default one"""
        
        self.error_messages = None
        
        if self.default_key and self.v_model == self.default_key:
            self.type='password'
            self.append_icon = 'mdi-eye-off'
        
        return self