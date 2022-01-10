from manim import *
import numpy as np
import json

class dater(ZoomedScene):

    def construct(self):

        # число векторов. задавать только четным.
        quantity = 10

        # замедление анимации
        zamedlenie = 0.5

        # длина основной анимации в секундах
        len_of_main_animation = 16

        # уменьшение портрета до размера экрана
        portrait_zoom = 0.0051

        # смещение рисунка в лево
        sdvig = 0

        ######################################################################################################################################
        # 1. Расчет длин векторов
        ######################################################################################################################################

        # файл со сглаженной прямой
        fp = open('portrait.json', 'r')

        # используется в расчете длин векторов (см. # 1.) и при отрисовки контура портрета (см. # 6.)
        data = np.array(json.load(fp))
        fp.close()

        res = data[:, 0]
        ims = -data[:, 1]

        cmplxs = res + 1j * ims
        phis = np.linspace(0, 2 * np.pi, len(data) + 1)[:-1]

        def cn(n):
            exparr = np.exp(-1j * n * phis)
            return (np.sum(exparr * cmplxs)) / len(data)

        cns = np.array([cn(i) for i in range(-quantity // 2, quantity // 2 + 1)])

        # разворачиваю список координат стрелок в нужном порядке - 0, 1, -1, 2, -2 ...
        cms = [0]
        for i in range(len(cns) // 2):
            cms.append(cns[quantity // 2 + 1 + i])
            cms.append(cns[quantity // 2 - 1 - i])
        cms = np.array(cms)

        # уменьшаю картинку до размера экрана
        list_c = cms * portrait_zoom

        ######################################################################################################################################
        # 2. Создаю список векторов
        ######################################################################################################################################

        # список векторов
        Arrow_list = [
            Arrow([0, 0, 0],
                  [sdvig, 0, 0],
                  buff=0,
                  color=WHITE,
                  max_stroke_width_to_length_ratio=1.5,
                  max_tip_length_to_length_ratio=0.15)
        ]

        ll = sdvig
        for i_arrow in range(quantity):
            # координаты конца i_arrow вектора
            ll += list_c[i_arrow + 1]

            # тут [i_arrow - 1] потому что вектор должен начинаться на конце предыдущего
            Arrow_list.append(Arrow(Arrow_list[i_arrow - 1 + 1].get_end(),
                                    [ll.real, ll.imag, 0],
                                    buff=0,
                                    color=WHITE,
                                    max_stroke_width_to_length_ratio=1.5,
                                    max_tip_length_to_length_ratio=0.15))

        ######################################################################################################################################
        # 3. Цикл создающий список скоростей
        ######################################################################################################################################

        # список скоростей вращения векторов
        list_rot_speed = []
        b = 1
        # цикл создающий список скоростей
        for i in range(quantity):
            list_rot_speed.append(b * (i + 1))
            b *= -1

        ######################################################################################################################################
        # 4. Код создающий список функций вращения векторов
        ######################################################################################################################################
        list_func = []

        # i_func - номер вектора, в списке векторов. rot_speed - нужная скорость вращения этого вектора
        def make_lambda(i_func, rot_speed, zamedlenie):
            # вращение вокруг конца предыдущего вектора
            return lambda mobj, dt: mobj.rotate(dt * rot_speed * zamedlenie,
                                                about_point=Arrow_list[i_func - 1].get_end())

        # создаю список функций
        for i in range(quantity):
            if i == 0:
                # первая функция будет вращать первый вектор вокруг конца неподвижного нулевого вектора
                list_func.append(lambda mobj, dt: mobj.rotate(dt * zamedlenie,
                                                              about_point=[sdvig, 0, 0]))
            else:
                list_func.append(make_lambda(i + 1, list_rot_speed[i], zamedlenie))

        ######################################################################################################################################
        # 5. Рисую вектора и трассировку конца последнего вектора
        ######################################################################################################################################

        self.wait(0.3)
        for i in range(quantity):
            self.add(Arrow_list[i + 1])

        # создаю трассировку конца последнего вектора желтым цветом
        self.add(TracedPath(Arrow_list[-1].get_end,
                            stroke_color='#D4FF00',
                            stroke_width=2))

        # вращение векторов. нулевой вектор не вращается
        for i in range(quantity):
            Arrow_list[i + 1].add_updater(list_func[0])
            for j in range(i):
                Arrow_list[i + 1].add_updater(list_func[j + 1])

        # длина основной анимации
        self.wait(len_of_main_animation)
