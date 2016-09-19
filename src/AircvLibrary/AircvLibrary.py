# -*- coding: utf-8 -*-
import os
import traceback
from time import sleep, time
import aircv as ac
from robot.libraries.BuiltIn import BuiltIn
import collections
from PIL import Image
from xml.etree import cElementTree as ET

global CUSTOMER_LIBRARY_NAME
CUSTOMER_LIBRARY_NAME = 'AppiumLibrary'
Display = collections.namedtuple('Display', ['width', 'height'])


class AircvLibrary(object):
    """ Wrapper Keywords for RobotFramework to click mobile screen, based on opencv & aircv.
    """

    def __init__(self):
        self.TH = 0.85  # THRESHOLD
        self._screen = ""
        self._timeout = 10
        self.img_path = ""
        self.output_dir = ""
        self._mobilelib = ""
        self._driver = ""
        """only can achieve BuiltIn().get_variables() at running time"""
        # sys_variables = BuiltIn().get_variables()
        # self.output_dir = os.path.abspath(sys_variables['${OUTPUTDIR}'])

    def _get_appium_handle(self):
        if not self._mobilelib:
            self._mobilelib = BuiltIn().get_library_instance(CUSTOMER_LIBRARY_NAME)
        if not self._driver:
            self._driver = self._mobilelib._current_application()

    def _capture_background(self, filename="screen.png"):
        """
        :param filename: the background screen
        :return: None
        """
        self._screen = os.path.join(self.output_dir, filename)
        self._mobilelib.capture_page_screenshot_without_html_log(os.path.join(self.output_dir, self._screen))

    def _prepare(self):
        """ update background  screen
        """
        self._get_appium_handle()

        if not self.output_dir:
            sys_variables = BuiltIn().get_variables()
            self.output_dir = os.path.abspath(sys_variables['${OUTPUTDIR}'])

        if os.path.isfile(self._screen):
            os.remove(self._screen)
        self._capture_background()

        start_time = time()
        while time() - start_time < self._timeout:
            if os.path.isfile(self._screen):
                return
            sleep(0.2)
            continue
        self._mobilelib._info("[>>>]:Capture Background failed")

    def mobile_image_threshold(self, threshold):
        self.TH = float(threshold)

    def mobile_image_set_timeout(self, time_num):
        """
        :param time_num:  wait in N secs to capture background screen
        :return: None
        """
        self._timeout = time_num

    def mobile_image_set_path(self, path='None'):
        """
        :param path: set the target image path
        :return: None
        """
        self.img_path = path

    def mobile_image_listdir(self):
        """show the target image directory's content
        """
        self._get_appium_handle()
        self._mobilelib._info("*" * 6)
        if self.img_path:
            self._mobilelib._info(self.img_path)
            self._mobilelib._info('-' * 6)
            content = os.listdir(self.img_path)
            if content.__len__() > 0:
                for item in content:
                    self._mobilelib._info(item)
            else:
                self._mobilelib._info("[>>>]:None Image")
        else:
            self._mobilelib._info("[>>>]:Image Path is NONE")
        self._mobilelib._info("*" * 6)

    def _image_click(self, target, index=1):
        """
        :param target: the target image that should be clicked
        :param index: select the N-th element
        :return: match info
        """
        index = int(index)
        self._prepare()
        if self.img_path:
            target = os.path.join(self.img_path, target)
        else:
            self._mobilelib._info("[>>>] img path not set")
        im_source = ac.imread(self._screen.decode('utf-8').encode('gbk'))
        im_search = ac.imread(target.decode('utf-8').encode('gbk'))
        result = ac.find_all_template(im_source, im_search, self.TH)

        result = sorted(result, key=lambda x: (x['result'][1], x['result'][0]))

        if index == 0:
            index = len(result) - 1
        else:
            index -= 1
        re = result[index]
        self._mobilelib._info(re)

        if self._mobilelib._is_android():
            self._mobilelib.click_a_point(re['result'][0], re['result'][1])
        if self._mobilelib._is_ios():
            _scale = self.scale()
            self._mobilelib.click_a_point(re['result'][0]/_scale, re['result'][1]/_scale)

        return re

    def mobile_click_image(self, target, index=1):
        """
        :param target: the target image that should be clicked
        :param index: select the N-th element; 0 -> the last one
        :return: match info
        """
        return self._image_click(target, index)

    def mobile_click_in(self, parent_image, sub_image):
        """ click  the sub image in the parent image
        """
        return self._parse_image_in(parent_image, sub_image, 'click')

    def mobile_get_image_location_in(self, parent_image, sub_image):
        """ get the sub image's coordinate which in the parent image
        """
        return self._parse_image_in(parent_image, sub_image, 'coordinate')

    def _parse_image_in(self, parent_image, sub_image, phase_type='click'):
        print 'Here is sub search img'
        self._prepare()
        if self.img_path:
            parent_image = os.path.join(self.img_path, parent_image)
            sub_image = os.path.join(self.img_path, sub_image)
        else:
            self._mobilelib._info("[>>>] img path not set")

        im_source = ac.imread(self._screen.decode('utf-8').encode('gbk'))
        im_parent = ac.imread(parent_image.decode('utf-8').encode('gbk'))
        im_sub = ac.imread(sub_image.decode('utf-8').encode('gbk'))
        intermediate = ac.find_template(im_source, im_parent, self.TH)
        in_rect = intermediate['rectangle']
        result = ac.find_all_template(im_source, im_sub, self.TH)

        for i in range(0, len(result), 1):
            result_rect = result[i]['rectangle']
            #  only cmp left-top  && right-down 's coordinate
            # rectangle[0~1]: left-top,left-down
            # rectangle[2~3]: right-top,right-down
            if self._coordinate_cmp(result_rect[0], in_rect[0]):  # left-top
                if self._coordinate_cmp(in_rect[3], result_rect[3]):  # right-down
                    try:
                        if 'click' in phase_type:
                            if self._mobilelib._is_android():
                                self._mobilelib.click_a_point(result[i]['result'][0], result[i]['result'][1])
                            if self._mobilelib._is_ios():
                                _scale = self.scale()
                                self._mobilelib.click_a_point(result[i]['result'][0]/_scale, result[i]['result'][1]/_scale)
                        elif 'coordinate' in phase_type:
                            if self._mobilelib._is_android():
                                return result[i]['result'][0], result[i]['result'][1]
                            if self._mobilelib._is_ios():
                                _scale = self.scale()
                                return result[i]['result'][0]/_scale, result[i]['result'][1]/_scale
                    except Exception, e:
                        print '[xxx]: %s ' % traceback.format_exc()
        # Todo : return valid value
        return -1

    def mobile_get_images_num(self, target):
        """ get sum of the image in current screen
        """
        return self._parse_images(target)

    def mobile_get_images_location(self, target, index=1):
        """ get  the N-th image's coordinate in current screen
        """
        return self._parse_images(target, index, 'location')

    def _parse_images(self, target, index=1, parse_type='num'):
        """[get the N-th image's coordinate] OR [the sum of the image]
        :param target: the target image that should be clicked
        :param index: select the N-th element; 0 -> the last one
        :return: the target Element's location:<x,y>
        """
        self._prepare()
        index = int(index)
        if self.img_path:
            target = os.path.join(self.img_path, target)
        else:
            self._mobilelib._info("[>>>] img path not set")
        im_source = ac.imread(self._screen.decode('utf-8').encode('gbk'))
        im_search = ac.imread(target.decode('utf-8').encode('gbk'))
        result = ac.find_all_template(im_source, im_search, self.TH)
        if 'num' in parse_type:
            return len(result)
        elif 'location' in parse_type:
            result = sorted(result, key=lambda x: (x['result'][1], x['result'][0]))
            if index == 0:
                index = len(result) - 1
            else:
                index -= 1
            re = result[index]
            self._mobilelib._info(re)

            if self._mobilelib._is_android():
                return re['result'][0], re['result'][1]
            if self._mobilelib._is_ios():
                _scale = self.scale()
                return re['result'][0]/_scale, re['result'][1]/_scale

    def mobile_screen_should_contain(self, target):
        """assert current  screen should contain target image
        """
        self._prepare()
        im_source = ac.imread(self._screen)
        im_search = ac.imread(target)
        re = ac.find_template(im_source, im_search, self.TH)
        if re:
            return True
        return False

    def mobile_screen_should_not_contain(self, target):
        """assert current  screen should  NOT contain target image
        """
        if self.mobile_screen_should_contain(target):
            return False
        return True

    def _coordinate_cmp(self, a, b):
        """
        @param a: (x0,y0)
        @param b: (x1,y1)
        @return: (x0>=x1) && (y0>=y1)? True:False
        """
        if len(a) == len(b):
            for i in range(0, len(a), 1):
                if a[i] < b[i]:
                    return False
        else:
            return False
        return True

    def scale(self):
        img = Image.open(self._screen)
        display = Display(*sorted(img.size))
        page = self._mobilelib.get_source()
        tree = ET.ElementTree(ET.fromstring(page))
        elem_of_UIAApplication = tree.find('UIAApplication')
        _width = elem_of_UIAApplication.attrib['width']
        _height = elem_of_UIAApplication.attrib['height']
        _scale = min(display) / min(int(_width), int(_height))
        return _scale
