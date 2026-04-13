local utils = import 'utils.libjsonnet';

{
  uses_user_defaults: true,
  description: 'Control a JLIP device such as a VCR.',
  keywords: ['command line', 'dvd', 'jlip', 'vcr', 'vhs'],
  project_name: 'vcrtool',
  version: '0.0.2',
  want_main: true,
  want_flatpak: true,
  publishing+: { flathub: 'sh.tat.vcrtool' },
  pyproject+: {
    project+: {
      scripts: {
        'capture-stereo': 'vcrtool.capture_stereo:main',
        jlip: 'vcrtool.main:jlip',
      },
    },
    tool+: {
      poetry+: {
        dependencies+: {
          'pyrate-limiter': utils.latestPypiPackageVersionCaret('pyrate-limiter'),
          anyio: utils.latestPypiPackageVersionCaret('anyio'),
          psutil: utils.latestPypiPackageVersionCaret('psutil'),
          pyftdi: utils.latestPypiPackageVersionCaret('pyftdi'),
          pyserial: utils.latestPypiPackageVersionCaret('pyserial'),
          pytimeparse2: utils.latestPypiPackageVersionCaret('pytimeparse2'),
        },
        group+: {
          dev+: {
            dependencies+: {
              'types-psutil': utils.latestPypiPackageVersionCaret('types-psutil'),
              'types-pyserial': utils.latestPypiPackageVersionCaret('types-pyserial'),
            },
          },
          tests+: {
            dependencies+: {
              'pytest-asyncio': utils.latestPypiPackageVersionCaret('pytest-asyncio'),
            },
          },
        },
      },
    },
  },
}
