# robotframework aircvlibrary
[![Documentation Status](https://readthedocs.org/projects/robotframework-aircvlibrary/badge/?version=latest)](http://robotframework-aircvlibrary.readthedocs.io/en/latest/?badge=latest)    [![Build Status](https://travis-ci.org/Netease-AutoTest/robotframework-aircvlibrary.svg?branch=master)](https://travis-ci.org/Netease-AutoTest/robotframework-aircvlibrary)    [![Latest Version](https://img.shields.io/pypi/v/robotframework-aircvlibrary.svg)](https://pypi.python.org/pypi/robotframework-aircvlibrary)     
Base on **aircv** and **opencv** library,wrap for **RobotFramework**.  
Click target screen area base on OpenCV algorithm.

## install
```pip install robotframework-aircvlibrary```

## keywords
- **mobile_click_image**(_target, index=1_)  
> ckick target area which match phone screen.

- **mobile_click_in**(_parent_image, sub_image_)
> click sub_area in special parent_area.   

- **mobile_get_images_location**(_target, index=1_)
> return the target img coordinate (_x, y_)

- [More tricks](http://robotframework-aircvlibrary.readthedocs.io/en/latest/usage.html)


## Todo
1. Add Web/ios support.  
2. Separate _match_ and _click_ method.<br>
due to diff platform depend on diff driver(appium/selenium2library).<br>
3. This lib may just return (_x,y_), call click method by yourself. 
