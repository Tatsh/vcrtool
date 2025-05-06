(import 'defaults.libjsonnet') + {
  // Project-specific
  description: 'Control a JLIP or SIRC-enabled device like a VCR.',
  keywords: ['command line', 'dvd', 'jlip', 'vcr', 'vhs'],
  project_name: 'vcrtool',
  version: '0.0.0',
  want_main: true,
  citation+: {
    'date-released': '2025-05-05',
  },
  pyproject+: {
    project+: {
      scripts: {
        'capture-stereo': 'vcrtool.capture_stereo:main',
        'jlip-presence-check': 'vcrtool.main:jlip_presence_check',
        jlip: 'vcrtool.main:jlip_commands',
        sircs: 'vcrtool.main:sircs',
      },
    },
    tool+: {
      poetry+: {
        dependencies+: {
          'pyrate-limiter': '^3.7.0',
          psutil: '^7.0.0',
          pyftdi: '^0.56.0',
          pyserial: '^3.5',
          pytimeparse2: '^1.7.1',
        },
        group+: {
          dev+: {
            dependencies+: {
              'types-psutil': '^7.0.0.20250401',
              'types-pyserial': '^3.5.0.20250326',
            },
          },
        },
      },
    },
  },
  // Common
  authors: [
    {
      'family-names': 'Udvare',
      'given-names': 'Andrew',
      email: 'audvare@gmail.com',
      name: '%s %s' % [self['given-names'], self['family-names']],
    },
  ],
  local funding_name = '%s2' % std.asciiLower(self.github_username),
  github_username: 'Tatsh',
  github+: {
    funding+: {
      ko_fi: funding_name,
      liberapay: funding_name,
      patreon: funding_name,
    },
  },
}
