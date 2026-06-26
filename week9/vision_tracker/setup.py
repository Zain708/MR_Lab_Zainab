from setuptools import find_packages, setup

package_name = 'vision_tracker'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Zainab',
    maintainer_email='zainabilas381@email.com',
    description='Computer vision tracking package for Mobile Robotics',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'camera_tracker = vision_tracker.camera_tracker:main',
            'multi_color_tracker = vision_tracker.multi_color_tracker:main'
        ],
    },
)