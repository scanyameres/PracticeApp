### Install Streamlit Authenticator

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/README.md

Install the package via pip.

```bash
pip install streamlit-authenticator
```

--------------------------------

### Hasher usage example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/utilities.md

Example showing how to hash a password, verify it, and pre-hash a credentials dict using Hasher methods.

```python
from streamlit_authenticator import Hasher

pwd = Hasher.hash('my_plain_password')
assert Hasher.check_pw('my_plain_password', pwd)
hashed_creds = Hasher.hash_passwords(config['credentials'])  # pre-hash a config dict
```

--------------------------------

### CloudModel constructor example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/cloud-model.md

Example of creating a CloudModel instance with an explicit server URL.

```python
from streamlit_authenticator.models.cloud import CloudModel

cloud = CloudModel(api_key='my-key', server_url='https://mkhorasani.pythonanywhere.com')
```

--------------------------------

### register_user example usage

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authentication-controller.md

Example call to register_user with pre-authorized email and callback, catching RegisterError.

```python
try:
    email, username, name = controller.register_user(
        'John', 'Smith', 'jsmith@gmail.com', 'jsmith',
        'Passw0rd!x', 'Passw0rd!x', 'my dog', pre_authorized=['jsmith@gmail.com'],
        callback=lambda payload: log(payload)
    )
except RegisterError as e:
    st.error(e)
```

--------------------------------

### Helpers usage example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/utilities.md

Shows reading a config file, updating credentials, generating a captcha image, and generating a random string.

```python
from streamlit_authenticator import Helpers

config = Helpers.read_config_file('config.yaml')
Helpers.update_config_file('config.yaml', 'credentials', config['credentials'])
st.image(Helpers.generate_captcha('login_captcha', 'secret'))
code = Helpers.generate_random_string(length=16)
```

--------------------------------

### Encryptor usage example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/utilities.md

Demonstrates creating an Encryptor with a secret key, encrypting a payload, and decrypting it back.

```python
from streamlit_authenticator import Encryptor

e = Encryptor('secret_key')
token = e.encrypt('sensitive payload')
plain = e.decrypt(token)
```

--------------------------------

### Example — dict initialization

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authenticate.md

Initializes Authenticate from a YAML config file, loading credentials and cookie settings. Requires the config.yaml file with credentials and cookie sections.

```python
import yaml
from yaml.loader import SafeLoader

with open('../config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    auto_hash=True
)
```

--------------------------------

### Usage example for CloudModel.send_email

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/endpoints.md

Python example showing how to send an email via CloudModel. Requires an API key and server URL; raises CloudError on failure. The example uses st.error, implying a Streamlit context.

```python
from streamlit_authenticator.models.cloud import CloudModel
from streamlit_authenticator.utilities import CloudError

cloud = CloudModel(api_key='my-key', server_url='https://mkhorasani.pythonanywhere.com')
try:
    cloud.send_email('2FA', 'user@example.com', '1234')
except CloudError as e:
    st.error(e)
```

--------------------------------

### Example — path initialization with error handling

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authenticate.md

Initializes Authenticate using a YAML config file path and a server URL, catching DeprecationError for legacy validator dicts.

```python
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import DeprecationError

try:
    authenticator = stauth.Authenticate('../config.yaml', server_url='https://mkhorasani.pythonanywhere.com')
except DeprecationError as e:
    print('Legacy validator dict:', e)
```

--------------------------------

### register_user pre-authorized registration example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authenticate.md

Example of registering a user with pre-authorized emails and captcha enabled. Displays a success message on success or an error message on exception.

```python
try:
    email, username, name = authenticator.register_user(
        pre_authorized=config['pre-authorized']['emails'],
        captcha=True
    )
    if email:
        st.success('User registered successfully')
except Exception as e:
    st.error(e)
```

--------------------------------

### send_email example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/cloud-model.md

Example of sending a 2FA email and handling CloudError.

```python
try:
    ok = cloud.send_email('2FA', 'user@example.com', '1234')
except CloudError as e:
    st.error(e)
```

--------------------------------

### MicrosoftModel instantiation example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/microsoft-model.md

Example of creating a MicrosoftModel instance with Microsoft OAuth2 configuration. The client_secret is optional and sent in the token exchange.

```python
from streamlit_authenticator.models.oauth2 import MicrosoftModel

model = MicrosoftModel({
    'client_id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
    'client_secret': 'secret',
    'redirect_uri': 'https://myapp.streamlit.app',
    'tenant_id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
})
```

--------------------------------

### logout usage example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authenticate.md

Example usage of the logout method, typically placed in the sidebar. Only renders the button when the user is authenticated.

```python
if st.session_state.get('authentication_status'):
    authenticator.logout(location='sidebar', key='Logout')
```

--------------------------------

### Basic login widget example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authenticate.md

Renders the login widget in the sidebar with captcha enabled. Handles authentication status: shows welcome message on success, error on failure, and warning when no attempt yet.

```python
try:
    authenticator.login(location='sidebar', captcha=True)
except Exception as e:
    st.error(e)

if st.session_state.get('authentication_status'):
    st.write(f"Welcome {st.session_state['name']}")
elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')
else:
    st.warning('Please enter your username and password')
```

--------------------------------

### Unrendered login example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authenticate.md

Runs login logic without a form, returning name, auth status, and username. Limits failed attempts to 5 and uses a custom widget key. Catches LoginError.

```python
try:
    name, auth_status, username = authenticator.login(location='unrendered', max_login_attempts=5, key='Login')
except LoginError as e:
    st.error(e)
```

--------------------------------

### Example — both providers

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authenticate.md

Shows how to call experimental_guest_login for both Google and Microsoft providers. The oauth2 parameter falls back to config['oauth2'] in path mode. The callback is called with {'widget': 'Guest login', 'email'} on success.

```python
try:
    authenticator.experimental_guest_login('Login with Google',
                                           provider='google',
                                           oauth2=config['oauth2'])
    authenticator.experimental_guest_login('Login with Microsoft',
                                           provider='microsoft',
                                           oauth2=config['oauth2'],
                                           roles=['viewer'])
except Exception as e:
    st.error(e)
```

--------------------------------

### CookieModel usage example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/cookie-model.md

Demonstrates creating a CookieModel, setting a cookie, retrieving it, and deleting it. Requires st.session_state['username'] to be set before set_cookie.

```python
from streamlit_authenticator.models import CookieModel

model = CookieModel('my_cookie', 'my_key', 30.0)
st.session_state['username'] = 'jsmith'
model.set_cookie()
payload = model.get_cookie()   # {'username': 'jsmith', 'exp_date': 1730...}
model.delete_cookie()
```

--------------------------------

### GoogleModel instantiation example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/google-model.md

Shows how to create a GoogleModel instance with client_id, client_secret, and redirect_uri. The client_secret is optional and sent during token exchange.

```python
from streamlit_authenticator.models.oauth2 import GoogleModel

model = GoogleModel({
    'client_id': 'xxx.apps.googleusercontent.com',
    'client_secret': 'GOCSPX-xxx',
    'redirect_uri': 'https://myapp.streamlit.app',
})
```

--------------------------------

### Full cookie lifecycle example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/cookie-controller.md

Shows the typical usage pattern: check for a valid re-auth token, log in, set a new cookie after successful login, and delete it on logout.

```python
if cc.get_cookie():            # valid re-auth token
    controller.login(token=cc.get_cookie())
    ...
cc.set_cookie()                # after successful login
cc.delete_cookie()             # on logout
```

--------------------------------

### login method usage example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authentication-controller.md

Shows how to call the login method with a username, password, max_login_attempts, captcha enabled, and the user's captcha input. The method returns a boolean indicating success or failure.

```python
ok = controller.login('jsmith', 'password123', max_login_attempts=3, captcha=True,
                      entered_captcha=user_captcha)
```

--------------------------------

### CookieController instantiation example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/cookie-controller.md

Creates a CookieController with explicit cookie name, key, and expiry days. This is used when no config file path is provided.

```python
from streamlit_authenticator.controllers import CookieController

cc = CookieController(
    cookie_name='my_cookie', cookie_key='my_secret_key', cookie_expiry_days=30.0
)
```

--------------------------------

### forgot_username usage example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authenticate.md

Example of calling forgot_username and handling the result. If username is truthy, shows success; otherwise shows error. Exceptions are caught and displayed.

```python
try:
    username, email = authenticator.forgot_username()
    if username:
        st.success('Username to be sent securely')
    else:
        st.error('Email not found')
except Exception as e:
    st.error(e)
```

--------------------------------

### Custom Validator Injection Example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/utilities.md

Shows how to inject a custom Validator subclass into Authenticate via the `validator` parameter. The example overrides `validate_password` to accept passwords of length 6 or more.

```python
from streamlit_authenticator.utilities import Validator

class MyValidator(Validator):
    def validate_password(self, password: str) -> bool:
        return len(password) >= 6

authenticator = Authenticate(config['credentials'], validator=MyValidator())
```

--------------------------------

### Example usage of update_user_details

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authenticate.md

Shows how to call update_user_details when the user is authenticated, displaying a success message on update and catching exceptions. The method requires the user to be logged in.

```python
if st.session_state.get('authentication_status'):
    try:
        if authenticator.update_user_details(st.session_state['username']):
            st.success('Entry updated successfully')
    except Exception as e:
        st.error(e)
```

--------------------------------

### forgot_password usage example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authenticate.md

Example of calling forgot_password with two_factor_auth and send_email enabled. The returned username indicates success; otherwise the username was not found. Exceptions are caught and displayed with st.error.

```python
try:
    username, email, new_password = authenticator.forgot_password(two_factor_auth=True,
                                                                  send_email=True)
    if username:
        st.success('New password sent securely')
    else:
        st.error('Username not found')
except Exception as e:
    st.error(e)
```

--------------------------------

### reset_password usage example

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authenticate.md

Shows how to call reset_password within a Streamlit app, checking authentication status and handling exceptions. Displays a success message on successful password modification and an error message on exception.

```python
if st.session_state.get('authentication_status'):
    try:
        if authenticator.reset_password(st.session_state['username']):
            st.success('Password modified successfully')
    except Exception as e:
        st.error(e)
```

--------------------------------

### Catching exceptions with try/except

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/errors.md

Shows how to import and catch specific exceptions from the top-level package or the utilities submodule. The example catches LoginError and RegisterError, but any exception subclass can be used. str(e) provides the error message.

```python
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import LoginError, RegisterError

try:
    authenticator.login()
except LoginError as e:
    st.error(e)          # str(e) is the message
```

--------------------------------

### register_user(location='main', pre_authorized=None, domains=None, fields=None, captcha=True, roles=None, merge_username_email=False, password_hint=True, two_factor_auth=False, clear_on_submit=False, key='Register user', callback=None) -> Tuple[str | None, str | None, str | None]

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/docs/index.rst

Renders a register new user widget. Returns a tuple containing the email, username, and name of the new user, or (None, None, None) if registration was not completed.

```APIDOC
## register_user(location='main', pre_authorized=None, domains=None, fields=None, captcha=True, roles=None, merge_username_email=False, password_hint=True, two_factor_auth=False, clear_on_submit=False, key='Register user', callback=None) -> Tuple[str | None, str | None, str | None]

### Description
Renders a register new user widget.

### Method
Widget method (Streamlit)

### Parameters
- **location** (Literal['main', 'sidebar']) - Optional, default='main' - Location where the registration widget is rendered.
- **pre_authorized** (List[str] | None) - Optional - List of emails of unregistered users who are authorized to register.
- **domains** (List[str] | None) - Optional - List of allowed email domains (e.g., ['gmail.com', 'yahoo.com']).
- **fields** (Dict[str, str] | None) - Optional - Custom labels for form fields and buttons.
- **captcha** (bool) - Optional, default=True - If True, requires captcha validation.
- **roles** (List[str] | None) - Optional - User roles for registered users.
- **merge_username_email** (bool) - Optional, default=False - If True, uses the email as the username.
- **password_hint** (bool) - Optional, default=True - If True, includes a password hint field.
- **two_factor_auth** (bool) - Optional, default=False - If True, enables two-factor authentication.
- **clear_on_submit** (bool) - Optional, default=False - If True, clears input fields after form submission.
- **key** (str) - Optional, default='Register user' - Unique key for the widget to prevent duplicate WidgetID errors.
- **callback** (Callable | None) - Optional - Function to execute when the form is submitted.

### Returns
- **tuple[str, str, str] or (None, None, None)** - Email, username, and name associated with the new user.
```

--------------------------------

### Implement register_user widget

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/README.md

Use the register_user widget to allow users to sign up. Optionally provide a pre_authorized list of emails to restrict registration to specific users.

```python
try:
    email_of_registered_user, \
    username_of_registered_user, \
    name_of_registered_user = authenticator.register_user(pre_authorized=config['pre-authorized']['emails'])
    if email_of_registered_user:
        st.success('User registered successfully')
except Exception as e:
    st.error(e)
```

--------------------------------

### Initialize Authentication Object

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/README.md

Import the configuration file and instantiate the Authenticate class. For large user bases, it is recommended to pre-hash passwords using Hasher.hash_passwords and set auto_hash to False.

```python
import yaml
from yaml.loader import SafeLoader

with open('../config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Pre-hashing all plain text passwords once
# stauth.Hasher.hash_passwords(config['credentials'])

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)
```

--------------------------------

### Helpers config file methods

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/utilities.md

Read, write, and update YAML config files. read uses SafeLoader, write uses default_flow_style=False and allow_unicode=True, update sets a key and writes back.

```python
@classmethod
def read_config_file(cls, path: str) -> dict:

@classmethod
def write_config_file(cls, path: str, config: dict) -> None:

@classmethod
def update_config_file(cls, path: str, key: str, items: dict) -> None:
```

--------------------------------

### Implement experimental_guest_login for OAuth2

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/README.md

Use this code to render guest login buttons for Google and Microsoft. Ensure the OAuth2 configuration parameters are correctly set in your config file before execution.

```python
try:
    authenticator.experimental_guest_login('Login with Google',
                                           provider='google',
                                           oauth2=config['oauth2'])
    authenticator.experimental_guest_login('Login with Microsoft',
                                           provider='microsoft',
                                           oauth2=config['oauth2'])
except Exception as e:
    st.error(e)
```

--------------------------------

### CloudModel.get_remote_variable

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/cloud-model.md

Cached GET of a flat key=value text file; returns the value of the specified variable if the file parses and the response status is 200.

```APIDOC
## CloudModel.get_remote_variable

### Description
Cached GET of a flat key=value text file; returns the value of the specified variable if the file parses and the response status is 200.

### Method
GET

### Signature
```python
@st.cache_data(show_spinner=False)
def get_remote_variable(_self, url: str, variable_name: str) -> str:
```

### Parameters
- **url** (str) - Required - URL of the remote variables file.
- **variable_name** (str) - Required - Name of the variable to retrieve.

### Returns
- **str** - Variable value, or `None` (implicitly) when not found.

### Throws
- **CloudError** - Any exception during the request; re-raised from the caught exception.
```

--------------------------------

### Encryptor.__init__

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/utilities.md

Initializes an Encryptor instance with a secret key, deriving a 32-byte Fernet key using SHA-256 and base64 URL-safe encoding.

```APIDOC
## Encryptor.__init__

### Description
Initializes an Encryptor instance with a secret key, deriving a 32-byte Fernet key using SHA-256 and base64 URL-safe encoding.

### Method
Constructor

### Signature
```python
def __init__(self, secret_key: str) -> None:
```

### Parameters
- **secret_key** (str) - Required - Any string; used to derive the Fernet key.

### Example
```python
from streamlit_authenticator import Encryptor

e = Encryptor('secret_key')
```
```

--------------------------------

### Instantiate AuthenticationController with credentials

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authentication-controller.md

Shows how to create an AuthenticationController instance by passing a credentials dictionary from a config object. The validator is set to None and auto_hash is enabled.

```python
from streamlit_authenticator.controllers import AuthenticationController

controller = AuthenticationController(
    credentials=config['credentials'],
    validator=None,
    auto_hash=True
)
```

--------------------------------

### Authenticate.experimental_guest_login

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/README.md

Creates a guest login button for OAuth2 authentication with Google or Microsoft. It allows non-registered users to log in and automatically registers their information in the credentials dictionary.

```APIDOC
## Authenticate.experimental_guest_login

### Description
Creates a guest login button for OAuth2 authentication with Google or Microsoft. It allows non-registered users to log in and automatically registers their information in the credentials dictionary.

### Method
POST

### Endpoint
/authenticate/experimental_guest_login

### Parameters
#### Path Parameters
- **button_name** (str) - Required - Rendered name of the guest login button. Default: 'Guest login'
- **location** (str) - Optional - Specifies the location of the guest login button. Options: 'main', 'sidebar'. Default: 'main'
- **provider** (str) - Optional - Selection for OAuth2 provider. Options: 'google', 'microsoft'. Default: 'google'
- **oauth2** (dict) - Optional - Configuration parameters to implement an OAuth2 authentication. Default: None
- **max_concurrent_users** (int) - Optional - Limits the number of concurrent users. If not specified there will be no limit. Default: None
- **single_session** (bool) - Optional - Disables the ability for the same user to log in multiple sessions. True: single session allowed, False: multiple sessions allowed. Default: False
- **roles** (list) - Optional - User roles for guest users. Default: None
- **use_container_width** (bool) - Optional - Button width setting. True: width will match container, False: width will fit to button contents. Default: False
- **callback** (callable) - Optional - Callback function that will be invoked on button press with a dict as a parameter. Default: None

### Request Example
```python
try:
    authenticator.experimental_guest_login('Login with Google',
                                           provider='google',
                                           oauth2=config['oauth2'])
    authenticator.experimental_guest_login('Login with Microsoft',
                                           provider='microsoft',
                                           oauth2=config['oauth2'])
except Exception as e:
    st.error(e)
```

### Response
#### Success Response (200)
- **user_info** (dict) - Information about the guest user, including name, email, and other details.

#### Response Example
{
  "user_info": {
    "name": "Guest User",
    "email": "guest@example.com"
  }
}
```

--------------------------------

### get_remote_variable method

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/cloud-model.md

Cached GET of a flat key=value text file; returns the value of variable_name if the file parses and response.status_code == 200. Throws CloudError on any request exception.

```python
@st.cache_data(show_spinner=False)
def get_remote_variable(_self, url: str, variable_name: str) -> str:
```

--------------------------------

### Example request to POST /send_email

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/endpoints.md

JSON body for the cloud email service's POST /send_email endpoint. Requires content, recipient, and email_type fields; email_type must be one of '2FA', 'PWD', or 'USERNAME'.

```json
{"content": "1234", "recipient": "user@example.com", "email_type": "2FA"}
```

--------------------------------

### Handle Authentication State and Logout

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/README.md

Use session state keys to check authentication status and render content or logout buttons accordingly.

```python
if st.session_state.get('authentication_status'):
    authenticator.logout()
    st.write(f'Welcome *{st.session_state.get("name")}*')
    st.title('Some content')
elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')
elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')
```

--------------------------------

### Authenticate.experimental_guest_login

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/docs/index.rst

Renders a guest login button for OAuth2 authentication. Supports configuration for provider, concurrent user limits, single session enforcement, roles, and callback execution.

```APIDOC
## Authenticate.experimental_guest_login

### Description
Renders a guest login button for OAuth2 authentication. Supports configuration for provider, concurrent user limits, single session enforcement, roles, and callback execution.

### Method
Method: experimental_guest_login

### Signature
experimental_guest_login(button_name: str = 'Guest login', location: Literal['main', 'sidebar'] = 'main', provider: Literal['google', 'microsoft'] = 'google', oauth2: Dict[str, Any] | None = None, max_concurrent_users: int | None = None, single_session: bool = False, roles: List[str] | None = None, use_container_width: bool = False, callback: Callable | None = None) -> None

### Parameters
- **button_name** (str, default='Guest login') - Display name for the guest login button.
- **location** (Literal['main', 'sidebar'], default='main') - Location where the guest login button is rendered.
- **provider** (Literal['google', 'microsoft'], default='google') - OAuth2 provider used for authentication.
- **oauth2** (dict, optional) - Configuration parameters for OAuth2 authentication.
- **max_concurrent_users** (int, optional) - Maximum number of users allowed to log in concurrently.
- **single_session** (bool, default=False) - If True, prevents users from logging into multiple sessions simultaneously.
- **roles** (list of str, optional) - Roles assigned to guest users.
- **use_container_width** (bool, default=False) - If True, the button width matches the container.
- **callback** (Callable, optional) - Function to execute when the button is pressed.

### Returns
None
```

--------------------------------

### Encryptor constructor

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/utilities.md

Initializes an Encryptor instance with a secret key. Derives a 32-byte key using SHA-256 and builds a Fernet cipher.

```python
def __init__(
        self,
        secret_key: str
        ) -> None:
```

--------------------------------

### Render Login Widget

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/README.md

Render the login widget using the authenticator object. Wrap the call in a try-except block to handle potential exceptions.

```python
try:
    authenticator.login()
except Exception as e:
    st.error(e)
```

--------------------------------

### login(location, max_concurrent_users, max_login_attempts, fields, captcha, single_session, clear_on_submit, key, callback)

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/docs/index.rst

Renders a login widget. Supports concurrent user limits, login attempt limits, captcha, single session enforcement, and callbacks.

```APIDOC
## login(location, max_concurrent_users, max_login_attempts, fields, captcha, single_session, clear_on_submit, key, callback)

### Description
Renders a login widget.

### Method
login

### Parameters
#### Parameters
- **location** (Literal['main', 'sidebar', 'unrendered']) - Optional, default='main' - Location where the login widget is rendered.
- **max_concurrent_users** (int | None) - Optional - Maximum number of users allowed to log in concurrently.
- **max_login_attempts** (int | None) - Optional - Maximum number of failed login attempts allowed.
- **fields** (Dict[str, str] | None) - Optional - Custom labels for form fields and buttons.
- **captcha** (bool) - Optional, default=False - If True, requires captcha validation.
- **single_session** (bool) - Optional, default=False - If True, prevents users from logging into multiple sessions simultaneously.
- **clear_on_submit** (bool) - Optional, default=False - If True, clears input fields after form submission.
- **key** (str) - Optional, default='Login' - Unique key for the widget to prevent duplicate WidgetID errors.
- **callback** (Callable | None) - Optional - Function to execute when the form is submitted.

### Returns
- If location='unrendered', returns (user's name, authentication status, username).
- Otherwise, returns None.

### Return Type
tuple[str, bool, str] or None
```

--------------------------------

### Helpers.write_config_file

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/utilities.md

Class method that writes a dictionary to a YAML config file.

```APIDOC
## Helpers.write_config_file

### Description
Class method that writes a dictionary to a YAML config file.

### Method
Class Method

### Signature
```python
@classmethod
def write_config_file(cls, path: str, config: dict) -> None:
```

### Parameters
- **path** (str) - Required - Path to the YAML config file.
- **config** (dict) - Required - Configuration dictionary to write.

### Returns
- **None**

### Example
```python
from streamlit_authenticator import Helpers

Helpers.write_config_file('config.yaml', config)
```
```

--------------------------------

### CloudModel.__init__

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/cloud-model.md

Initializes a CloudModel instance with an API key and optional server URL. If no server URL is provided, it fetches the remote 2FA/email server address from a remote variables file.

```APIDOC
## CloudModel.__init__

### Description
Initializes a CloudModel instance with an API key and optional server URL. If no server URL is provided, it fetches the remote 2FA/email server address from a remote variables file.

### Method
Constructor

### Signature
```python
def __init__(
        _self,
        api_key: str,
        server_url: Optional[str] = None
        ) -> None:
```

### Parameters
- **api_key** (str) - Required - API key sent as a `Bearer` token on email requests.
- **server_url** (Optional[str]) - Optional - Cloud server base URL; when `None`, resolved from the remote variables file.

### Throws
- **CloudError** - Remote-variable fetch fails (any exception from `requests.get`); the message is the underlying exception text and a hint to pass `server_url` manually.

### Example
```python
from streamlit_authenticator.models.cloud import CloudModel

cloud = CloudModel(api_key='my-key', server_url='https://mkhorasani.pythonanywhere.com')
```
```

--------------------------------

### register_user

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authenticate.md

Renders the new-user registration widget. Returns the new user's email, username, and name, or None values if the form was not submitted.

```APIDOC
## register_user

### Description
Renders the new-user registration widget. Returns the new user's email, username, and name, or None values if the form was not submitted.

### Method
register_user

### Parameters
- **location** (Literal['main', 'sidebar']) - Default: 'main' - Widget location.
- **pre_authorized** (Optional[List[str]]) - Default: None - Emails allowed to register; None allows anyone. bool/dict → DeprecationError.
- **domains** (Optional[List[str]]) - Default: None - Required email domains, e.g. ['gmail.com', 'yahoo.com'].
- **fields** (Optional[Dict[str, str]]) - Default: None - Custom labels; default dict in source (line 458).
- **captcha** (bool) - Default: True - Captcha required (note: default True, unlike other widgets).
- **roles** (Optional[List[str]]) - Default: None - Roles for the new user.
- **merge_username_email** (bool) - Default: False - If True, username = entered email (one field).
- **password_hint** (bool) - Default: True - Show the password-hint field.
- **two_factor_auth** (bool) - Default: False - If True, verifies an emailed code first (requires api_key).
- **clear_on_submit** (bool) - Default: False - Form clear-on-submit.
- **key** (str) - Default: 'Register user' - Widget key.
- **callback** (Optional[Callable]) - Default: None - Called with `{'widget': 'Register user', 'new_name', 'new_last_name', 'new_email', 'new_username'}`.

### Returns
(email, username, "First Last") of the new user, or (None, None, None) when the form was not submitted.

### Throws
- **DeprecationError** - pre_authorized given as bool or dict.
- **RegisterError** - Validation failures (names, email, domain, username, passwords, hint, captcha, uniqueness, pre-authorization) — conditions in errors.md.
- **LoginError** - 'Roles must be provided as a list'.
- **CloudError** - 2FA email-sending failure.

### Example — pre-authorized registration
```python
try:
    email, username, name = authenticator.register_user(
        pre_authorized=config['pre-authorized']['emails'],
        captcha=True
    )
    if email:
        st.success('User registered successfully')
except Exception as e:
    st.error(e)
```
```

--------------------------------

### Validator Constructor

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/utilities.md

Initializes the Validator class with no arguments.

```python
def __init__(self):
```

--------------------------------

### Authenticate.__init__

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authenticate.md

Constructor for the top-level Authenticate class. Initializes the authentication view with credentials, cookie settings, and optional validator and API key.

```APIDOC
## Authenticate.__init__

### Description
Constructor for the top-level Authenticate class. Initializes the authentication view with credentials, cookie settings, and optional validator and API key.

### Method
Constructor

### Signature
```python
def __init__(
        self,
        credentials: Union[Dict[str, Any], str],
        cookie_name: str = 'some_cookie_name',
        cookie_key: str = 'some_key',
        cookie_expiry_days: float = 30.0,
        validator: Optional[Validator] = None,
        auto_hash: bool = True,
        api_key: Optional[str] = None,
        **kwargs: Optional[Dict[str, Any]]
        ) -> None:
```

### Parameters
- `credentials` (Union[Dict[str, Any], str]) - Required - Credentials dict or path to a YAML config file (path mode reads cookie and API-key settings from the file).
- `cookie_name` (str) - Optional - Default: `'some_cookie_name'` - Name of the re-authentication cookie stored in the client's browser.
- `cookie_key` (str) - Optional - Default: `'some_key'` - Secret key used for encrypting the re-authentication cookie (JWT signing + Fernet encryption).
- `cookie_expiry_days` (float) - Optional - Default: `30.0` - Expiry time for the re-authentication cookie in days. A value of `0` disables cookie creation (see `CookieModel.set_cookie`).
- `validator` (Optional[Validator]) - Optional - Default: `None` - Custom `Validator`; `None` creates a default `Validator()`.
- `auto_hash` (bool) - Optional - Default: `True` - If `True`, plain-text passwords in the credentials are automatically bcrypt-hashed at construction time.
- `api_key` (Optional[str]) - Optional - Default: `None` - API key for cloud-server features (two-factor codes, password/username emails).
- `**kwargs` (Optional[Dict[str, Any]]) - Optional - Stored in `self.attrs`. Recognized keys: `server_url` (cloud email server URL), `password_instructions` (password-field help text; falls back to `params.PASSWORD_INSTRUCTIONS`), `login_sleep_time` (sleep before showing login; falls back to `params.PRE_LOGIN_SLEEP_TIME`).

### Returns
`None`. Construction creates these attributes: `api_key`, `attrs` (the `**kwargs`), `secret_key` (the `cookie_key`), `path` (`credentials` when a string path), `cookie_controller`, `authentication_controller`, `encryptor`.

### Throws
**`DeprecationError`** — raised when `validator` is passed as a `dict` (the legacy `pre_authorized` dict); message points to `params.REGISTER_USER_LINK`.

### Example — dict initialization
```python
import yaml
from yaml.loader import SafeLoader

with open('../config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    auto_hash=True
)
```

### Example — path initialization with error handling
```python
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import DeprecationError

try:
    authenticator = stauth.Authenticate('../config.yaml', server_url='https://mkhorasani.pythonanywhere.com')
except DeprecationError as e:
    print('Legacy validator dict:', e)
```
```

--------------------------------

### Helpers generate_random_string method

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/utilities.md

Generates a random string from selected character sets. Punctuation excludes '<' and '>', spaces removed. length=0 yields empty string; empty sets raise IndexError.

```python
@classmethod
def generate_random_string(cls, length: int=16, letters: bool=True, digits: bool=True,
                           punctuation: bool=True) -> str:
```

--------------------------------

### Import Streamlit Authenticator

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/README.md

Import the module to begin using authentication features in your Streamlit application.

```python
import streamlit as st
import streamlit_authenticator as stauth
```

--------------------------------

### YAML configuration file structure

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/README.md

The configuration file includes cookie settings, user credentials with roles, optional OAuth2 provider details, and a list of pre-authorized emails.

```yaml
cookie:
  expiry_days: 30
  key: # To be filled with any string
  name: # To be filled with any string
credentials:
  usernames:
    jsmith:
      email: jsmith@gmail.com
      failed_login_attempts: 0 # Will be managed automatically
      first_name: John
      last_name: Smith
      logged_in: False # Will be managed automatically
      password: abc # Will be hashed automatically
      roles: # Optional
      - admin
      - editor
      - viewer
    rbriggs:
      email: rbriggs@gmail.com
      failed_login_attempts: 0 # Will be managed automatically
      first_name: Rebecca
      last_name: Briggs
      logged_in: False # Will be managed automatically
      password: def # Will be hashed automatically
      roles: # Optional
      - viewer
oauth2: # Optional
  google: # Follow instructions: https://developers.google.com/identity/protocols/oauth2
    client_id: # To be filled
    client_secret: # To be filled
    redirect_uri: # URL to redirect to after OAuth2 authentication
  microsoft: # Follow instructions: https://learn.microsoft.com/en-us/graph/auth-register-app-v2
    client_id: # To be filled
    client_secret: # To be filled
    redirect_uri: # URL to redirect to after OAuth2 authentication
    tenant_id: # To be filled
pre-authorized: # Optional
  emails:
  - melsby@gmail.com
api_key: # Optional - (phased out)
```

--------------------------------

### Validator.__init__

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/utilities.md

Constructor for the Validator class. Initializes a new instance with no arguments.

```APIDOC
## Validator.__init__

### Description
Initializes a new Validator instance. No arguments are required.

### Method
Constructor

### Signature
```python
def __init__(self):
```

### Parameters
None

### Returns
None
```

--------------------------------

### Constructor Signature

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authenticate.md

Defines the constructor with parameters for credentials, cookie settings, validator, auto-hash, and API key.

```python
def __init__(
        self,
        credentials: Union[Dict[str, Any], str],
        cookie_name: str = 'some_cookie_name',
        cookie_key: str = 'some_key',
        cookie_expiry_days: float = 30.0,
        validator: Optional[Validator] = None,
        auto_hash: bool = True,
        api_key: Optional[str] = None,
        **kwargs: Optional[Dict[str, Any]]
        ) -> None:
```

--------------------------------

### experimental_guest_login method signature

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authenticate.md

Defines the experimental_guest_login method with parameters for guest login via OAuth2. It renders a guest-login button and returns None. Throws LoginError on failures such as captcha, concurrent users, existing user, sessions, or roles list.

```python
def experimental_guest_login(self, button_name: str='Guest login',
                             location: Literal['main', 'sidebar'] = 'main',
                             provider: Literal['google', 'microsoft'] = 'google',
                             oauth2: Optional[Dict[str, Any]] = None,
                             max_concurrent_users: Optional[int]=None,
                             single_session: bool=False, roles: Optional[List[str]]=None,
                             use_container_width: bool=False,
                             callback: Optional[Callable]=None) -> None:
```

--------------------------------

### register_user method signature

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authenticate.md

Renders the new-user registration widget. Returns (email, username, 'First Last') of the new user, or (None, None, None) when the form was not submitted. Throws DeprecationError, RegisterError, LoginError, or CloudError under the conditions listed in the parameters.

```python
def register_user(self, location: Literal['main', 'sidebar'] = 'main',
                  pre_authorized: Optional[List[str]] = None,
                  domains: Optional[List[str]] = None, fields: Optional[Dict[str, str]] = None,
                  captcha: bool = True, roles: Optional[List[str]] = None,
                  merge_username_email: bool = False, password_hint: bool = True,
                  two_factor_auth: bool = False, clear_on_submit: bool = False,
                  key: str = 'Register user', callback: Optional[Callable] = None
                  ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
```

--------------------------------

### Helpers.read_config_file

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/utilities.md

Class method that reads a YAML config file and returns its contents as a dictionary.

```APIDOC
## Helpers.read_config_file

### Description
Class method that reads a YAML config file and returns its contents as a dictionary.

### Method
Class Method

### Signature
```python
@classmethod
def read_config_file(cls, path: str) -> dict:
```

### Parameters
- **path** (str) - Required - Path to the YAML config file.

### Returns
- **dict** - Parsed YAML content.

### Example
```python
from streamlit_authenticator import Helpers

config = Helpers.read_config_file('config.yaml')
```
```

--------------------------------

### CloudModel constructor

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/cloud-model.md

Initializes a CloudModel instance with an API key and optional server URL. When server_url is None, it fetches the remote 2FA server address from the remote variables file. Throws CloudError if the remote-variable fetch fails.

```python
def __init__(
        _self,
        api_key: str,
        server_url: Optional[str] = None
        ) -> None:
```

--------------------------------

### register_user

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/authentication-model.md

Registers a new user with the provided details, handling pre-authorization and persistence. Returns a tuple of the user's email, username, and full name.

```APIDOC
## register_user

### Description
Registers a new user with the provided details, handling pre-authorization and persistence. Returns a tuple of the user's email, username, and full name.

### Method
register_user

### Signature
```python
def register_user(self, new_first_name: str, new_last_name: str, new_email: str,
                  new_username: str, new_password: str, password_hint: str,
                  pre_authorized: Optional[List[str]] = None,
                  roles: Optional[List[str]] = None,
                  callback: Optional[Callable] = None) -> Tuple[str, str, str]:
```

### Parameters
- **new_first_name** (str) - Required - The first name of the new user.
- **new_last_name** (str) - Required - The last name of the new user.
- **new_email** (str) - Required - The email address of the new user.
- **new_username** (str) - Required - The username for the new user.
- **new_password** (str) - Required - The password for the new user.
- **password_hint** (str) - Required - A hint for the password.
- **pre_authorized** (Optional[List[str]]) - Optional - List of pre-authorized emails. If None, falls back to config['pre-authorized']['emails'] when a config path exists.
- **roles** (Optional[List[str]]) - Optional - List of roles assigned to the new user.
- **callback** (Optional[Callable]) - Optional - A callback function invoked with a dictionary containing user registration details.

### Returns
`Tuple[str, str, str]` — `(email, username, f'{first_name} {last_name}')`.

### Throws
| Exception | Condition |
|-----------|-----------|
| `RegisterError` | `'Email already taken'` (email exists anywhere in credentials), `'Username/email already taken'` (username taken), `'User not pre-authorized to register'` (email not in the `pre_authorized` list). |

### Behavior
- When `pre_authorized` is `None` and a config path exists, falls back to `config['pre-authorized']['emails']`.
- If `pre_authorized` is a list and the email is in it: registers, removes the email from the list, and persists `pre-authorized` to the config file.
- `_register_credentials` stores `{'email', 'logged_in': False, 'first_name', 'last_name', 'password': Hasher.hash(...), 'roles', 'password_hint'?}`.
- Callback payload: `{'widget': 'Register user', 'new_name', 'new_last_name', 'new_email', 'new_username'}`.
```

--------------------------------

### Update configuration file

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/README.md

Persist changes to the configuration file by re-saving it after modifications or widget usage. This step is unnecessary if the config file path is provided directly to the Authenticate class.

```python
with open('../config.yaml', 'w') as file:
    yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
```

--------------------------------

### CookieModel constructor

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/cookie-model.md

Initializes the CookieModel. When 'path' is set, cookie settings are loaded from config['cookie']; otherwise the passed values are used. Instantiates stx.CookieManager() and initializes self.token and self.exp_date.

```python
def __init__(
        self,
        cookie_name: Optional[str] = None,
        cookie_key: Optional[str] = None,
        cookie_expiry_days: Optional[float] = None,
        path: Optional[str] = None
        ) -> None:
```

--------------------------------

### MicrosoftModel.__init__

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/api-reference/microsoft-model.md

Initializes the MicrosoftModel with Microsoft OAuth2 configuration. Sets the configuration dictionary and initializes the code verifier to None.

```APIDOC
## MicrosoftModel.__init__

### Description
Initializes the MicrosoftModel with Microsoft OAuth2 configuration. Sets the configuration dictionary and initializes the code verifier to None.

### Method
Constructor

### Signature
```python
def __init__(
        self,
        microsoft: Dict[str, str]
        ) -> None:
```

### Parameters
- **microsoft** (Dict[str, str]) - Required - Microsoft OAuth2 config: `client_id` (required), `tenant_id` (required), `redirect_uri` (required), `client_secret` (optional — sent in the token exchange).

### Example
```python
from streamlit_authenticator.models.oauth2 import MicrosoftModel

model = MicrosoftModel({
    'client_id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
    'client_secret': 'secret',
    'redirect_uri': 'https://myapp.streamlit.app',
    'tenant_id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
})
```
```

--------------------------------

### CloudModel Constructor

Source: https://github.com/mkhorasani/streamlit-authenticator/blob/main/_autodocs/configuration.md

Constructor options for the CloudModel class, including API key and server URL.

```APIDOC
## CloudModel Constructor

### Description
Constructor options for the CloudModel class, including API key and server URL.

### Parameters
- **api_key** (`str`) - Required - Bearer token for email API.
- **server_url** (`Optional[str]`) - Optional (default: `None`) - Base URL; fetched remotely when `None`.
```