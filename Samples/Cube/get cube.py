from TM1py.Services import CubeService
from TM1py.Services import LoginService
from TM1py.Services import RESTService

login = LoginService.native('admin', 'apple')

with RESTService(ip='', port=8001, login=login, ssl=False) as tm1_rest:
    cube_service = CubeService(tm1_rest)
    c = cube_service.get('Rubiks Cube')
    print(c.name)
    print(c.dimensions)
    if c.has_rules:
        print(c.rules)