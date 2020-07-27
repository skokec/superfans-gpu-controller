from setuptools import setup
setup(name='superfans-gpu-controller',
      version='0.1',
      description='Supermicro FAN controller based on NVIDIA GPU temperature',
      py_modules=['superfans_gpu_controller','superfans' ],
      entry_points={
          'console_scripts': [
              'superfans-gpu-controller = superfans_gpu_controller:main',
          ],
      },
     )
