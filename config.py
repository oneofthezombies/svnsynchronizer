__ROOT_DIR = 'C:\\Users\\hunho\\repo\\test-svn-root'
__BASE_URL = 'http://host.docker.internal/svn/Abyss'

REPOSITORIES = [
    {
        'path': f'{__ROOT_DIR}/trunkCertification',
        'url': f'{__BASE_URL}/trunk/Abyss/Projects/iOS/Certification',
        'clean': True
    },
    {
        'path': f'{__ROOT_DIR}/Trunk/Abyss',
        'url': f'{__BASE_URL}/trunk/Abyss',
        'clean': True
    },
    {
        'path': f'{__ROOT_DIR}/Trunk/Packages',
        'url': f'{__BASE_URL}/trunk/Packages',
        'clean': True
    },
    {
        'path': f'{__ROOT_DIR}/KR_Beta/Abyss',
        'url': f'{__BASE_URL}/branches/KR_Beta/Abyss',
        'clean': True
    },
    {
        'path': f'{__ROOT_DIR}/KR_Beta/Packages',
        'url': f'{__BASE_URL}/branches_res/KR_Beta/Packages',
        'clean': True
    },
]
