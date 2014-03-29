#coding=utf-8

import cv2,cv
import numpy as np
import coconut as co
import math

LIMIT_CAUGHT = 70
DEVIATION_BETWEEN_X = 3
DEVIATION_BETWEEN_Y = 3
ANGLE_GAP = 12

#input <"int">
def set_limit_caught(new_limit):
    '''重新指定识别轮廓的识别下限'''
    global LIMIT_CAUGHT
    LIMIT_CAUGHT = new_limit


#input <"float"> or <"int">
def set_deviation_x(new_deviation_x):
    '''重新指定识别横线与横线之间的误差距离'''
    global DEVIATION_BETWEEN_X
    DEVIATION_BETWEEN_X = new_deviation_x


#input <"float"> or <"int">
def set_deviation_y(new_deviation_y):
    '''重新指定识别纵线与纵线之间的误差距离'''
    global DEVIATION_BETWEEN_Y
    DEVIATION_BETWEEN_Y = new_deviation_y


#input <"float"> or <"int">
def set_deviation(new_deviation_x, new_deviation_y):
    '''一次性重新指定识别横纵误差距离'''
    global DEVIATION_BETWEEN_X, DEVIATION_BETWEEN_Y
    DEVIATION_BETWEEN_X = new_deviation_x
    DEVIATION_BETWEEN_Y = new_deviation_y



#input <"float"> or <"int">
#best between 0-20 degree
def set_angle_gap(new_angle_gap):
    '''重新指定角度分类的角度度数误差值'''
    global ANGLE_GAP
    ANGLE_GAP = new_angle_gap


#open an image as <"numpy.ndarray">
#input address<"string">
#output image<"numpy.ndarray">
#<"numpy.ndarray">.dtype = unit8 (0-255)
#<"numpy.ndarray">.shape = (width, height, <3 is the Count of BGR>)
def open_image(address):
    '''打开图像为numpy.ndarray类型矩阵'''
    return cv2.imread(address)


#save <"numpy.ndarray"> as an image
#input output_address<"string">
#input image<"numpy.ndarray">
def save_image(address,img):
    '''将numpy.ndarray类型的图像保存成硬图像文件'''
    cv2.imwrite(address,img)


#copy img.shape to create a vain paper
#0 mains Black and 255 mains White
#input1 shape<"tuple"> = <"numpy.ndarray">.shape = (width, height, <3 is the Count of BGR>)
#input2 color<"int"> = 0-255
def create_paper(shape, color=0):
    '''根据长宽与颜色来预设生成一张画布'''
    return np.zeros(shape, np.uint8) + color


#input image <"numpy.ndarray">
#image.shape = (width, height) or (width, height, 3)
#input threshold_value <"int"> 0-255 or <"unit8">
#output black_and_white_image <"numpy.ndarray">
#black_and_white_image.shape = (width, height, 3) (RGB)
def get_black_and_white_image(image, threshold_value):
    '''根据阈值将图像二值化处理，即将输入图像处理成黑白图像'''
    ret,thresh = cv2.threshold(img, threshold_value, 255, cv2.THRESH_BINARY)
    return thresh


#input a colorful image
#input_image.shape = (width, height, <3 is the Count of BGR>)
#output a gray image
#output_image.shape = (width, height)
#input <"numpy.ndarray"> and output <"numpy.ndarray">
def get_gray_image(image):
    '''将RGB格式图像转换成灰度图像'''
    return cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)


#input image <"numpy.ndarray">
#output image <"numpy.ndarray">
def get_thick(img, a):
    '''腐蚀图像 = 加粗图像线条'''
    #OpenCV定义的结构元素
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (a, a))
    #腐蚀图像=加粗
    eroded = cv2.erode(img, kernel)
    return eroded


#input image <"numpy.ndarray">
#output image <"numpy.ndarray">
def get_thin(img, a):
    '''膨胀图像 = 变细图像线条'''
    #OpenCV定义的结构元素
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (a, a))
    #膨胀图像 = 变细
    dilated = cv2.dilate(img, kernel)
    return dilated


#input image <"numpy.ndarray">
#output image <"numpy.ndarray">
def close_gap(img, a):
    '''缝合缺口 = 先加粗a个单位，再变细a个单位'''
    img_thick = get_thick(img, a)
    img_thin = get_thin(img_thick, a)
    return img_thin


#input1 img_gray <"numpy.ndarray"> which shape is just (width, height)
#input2 img_draw is for the contours to be drawt on
#output cornerlists=[cornerlist1,cornerlist2...]
#cornerlist[i]=[(x1,y1), (x2,y2), (x3,y3)...]
def get_contour_cornerlists(img_gray, img_draw=None):
    '''根据灰度图片识别出所有的内轮廓的点集'''
    global LIMIT_CAUGHT
    cornerlists = []
    ret, thresh = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh,2,1)
    for kk in range(len(contours)):
        cnt = contours[kk]
        #set_limit_caught() can change the value of LIMIT_CAUGHT
        if len(cnt) > LIMIT_CAUGHT:
            if hierarchy[0][kk][0] == -1:
                break
            zywcorners = []
            for i in range(len(cnt)-1):
                start = cnt[i][0]
                end =  cnt[i+1][0]
                zywcorners.append((end[0],end[1]))
                if not img_draw == None:
                    cv2.line(img_draw,(start[0],start[1]),(end[0],end[1]),[0,255,0],2)
                    cv2.circle(img_draw,(start[0],start[1]),1,[0,0,255],-1)
            start = cnt[0][0]
            zywcorners.append((start[0],start[1]))
            if not img_draw == None:
                cv2.circle(img_draw,(end[0],end[1]),1,[0,0,255],-1)
                cv2.line(img_draw,(start[0],start[1]),(end[0],end[1]),[0,255,0],2)
            cornerlists.append(zywcorners)
    return cornerlists


#get a uniformal rectangle
#input a contour list [(x1,y1), (x2,y2)...]
#output rectangle<"list"> [center(x,y),size(width,height),angle]
def get_rectangle(contour):
    '''根据一个矩形内轮廓角点集识别出此矩形'''
    rect = cv.MinAreaRect2(contour)
    #get the uniform angle
    if rect[2]<-45:
        rect = [rect[0],(rect[1][1],rect[1][0]),rect[2]+90]
    elif rect[2]>45:
        rect = [rect[0],(rect[1][1],rect[1][0]),rect[2]-90]
    else:
        rect = [rect[0],rect[1],rect[2]]
    return rect


#input a list of rectangles
#output <"list"> = [ [rect1,rect2...], [rect8, rect9..]..]
#output's every rect is not a list but a tuple
#recti = (center(x,y), size(width,height), angle_adjusted)
def machine_classify(rectangles):
    '''根据矩形的角度对矩形进行角度优化与分类'''
    #set_angle_gap() can change the value of ANGLE_GAP
    global ANGLE_GAP
    angle_gap = ANGLE_GAP #
    rects = []
    angles = []
    def dishave_angle(angle_test):
        if len(angles) == 0:
            return None
        for angle_i in range(len(angles)):
            if abs(angles[angle_i]-angle_test) < angle_gap:
                return angle_i
        return None

    for rectangle in rectangles:
        i = dishave_angle( rectangle[2] )
        if i > -1 :
            angles[i] = (angles[i]*len(rects[i])+rectangle[2])/float(len(rects[i])+1)
            rects[i].append((rectangle[0],rectangle[1],angles[i]))
        else:
            angles.append( rectangle[2] )
            rects.append( [(rectangle[0], rectangle[1], rectangle[2])] )

    for i in range(len(rects)):
        for j in range(len(rects[i])):
            rects[i][j] = (rects[i][j][0], rects[i][j][1], angles[i])

    return rects


#input <"list"> = [ [rect1,rect2...], [rect8, rect9..]..]
#input recti = (center(x,y), size(width,height), angle_adjusted)
#output <"list"> = [ [rect1,rect2...], [rect8, rect9..]..]
#output recti = (point1, point2, point3, point4)
def machine_optimize(rectangles):
    '''对列表中的矩形进行边角重合并线优化'''
    #get four points of rectangles
    four_points = []
    for rectangle_list in rectangles:
        four_points.append( [] )
        for rectangle in rectangle_list:
            four_points[-1].append( cv2.cv.BoxPoints(rectangle) )

    #do with every kinds of angle
    four_points_adjusted = []
    for i in range(len(rectangles)):
        #adjust_rect_list( angle,rect_list )
        four_points_adjusted.append( adjust_rect_list(rectangles[i][0][2], four_points[i]) )

    return four_points_adjusted


#input one rectangle list
#input  <"list"> = [rect1,rect2...]
#input recti = (point1, point2, point3, point4)
#output <"list"> = [rect1_adjusted,rect2_adjusted...]
def adjust_rect_list(angle, rectangle_list):
    '''边角重合并线优化的核心处理函数（重要）'''
    
    global DEVIATION_BETWEEN_X, DEVIATION_BETWEEN_Y
    
    #input gap_on_y
    #hide_input <"list"> = [ a1, a2 ,a3 ...]
    #output <"list"> = [ <[a1,a2...]>, <[a11, a12..]> ..]
    #output <"list"> = [ a1_, a2_ ..]
    def machine_classify_crossing_y(gap_on_y):
        rails = []
        for y in crossing_y:
            true = 1
            for rail in rails:
                if co.distance_y(angle, y[0], rail[0]) < gap_on_y:
                    rail[0] = ((len(rail)-1)*rail[0]+y[0])/float(len(rail))
                    rail.append(y[1])
                    true = None
            if true:rails.append(y)
        return rails

    #get the crossing point of y-axis
    sum = 0
    crossing_y = []
    for rect in rectangle_list:
        sum = sum+1
        #mean which rect and which side
        crossing_y.append( [co.crossy(angle, rect[0]), sum] ) #up
        crossing_y.append( [co.crossy(angle, rect[1]),-sum] ) #down
    
    #classify the crossing_y 横线与横线间的误差
    #set_deviation_x() can change the value of DEVIATION_BETWEEN_X
    rails_on_y = machine_classify_crossing_y( DEVIATION_BETWEEN_X )
    #adjust the crossing_y
    for rail in rails_on_y:
        if len(rail)>2:
            bb=rail[0]
            for i in range(len(rail)-1):
                kk=abs(rail[i+1])-1 #give back for before
                if rail[i+1]>0: #up and down
                    rectangle_list[kk]=co.adjust(angle,bb,rectangle_list[kk],2)#up 0 3
                else:
                    rectangle_list[kk]=co.adjust(angle,bb,rectangle_list[kk],1)#down 1 2

    ###from crossing_y to crossing_x

    #input gap_on_x
    #hide_input <"list"> = [ a1, a2 ,a3 ...]
    #output <"list"> = [ <[a1,a2...]>, <[a11, a12..]> ..]
    #output <"list"> = [ a1_, a2_ ..]
    def machine_classify_crossing_x(gap_on_x):
        rails = []
        for x in crossing_x:
            true = 1
            for rail in rails:
                if co.distance_x(angle+90, x[0], rail[0]) < gap_on_x:
                    rail[0] = ((len(rail)-1)*rail[0]+x[0])/float(len(rail))
                    rail.append(x[1])
                    true = None
            if true:rails.append(x)
        return rails

    #get the crossing point of y-axis
    sum = 0
    crossing_x = []
    for rect in rectangle_list:
        sum = sum+1
        #mean which rect and which side
        crossing_x.append( [co.crossx(angle+90, rect[1]), sum] ) #left
        crossing_x.append( [co.crossx(angle+90, rect[2]),-sum] ) #right

    #classify the crossing_x 竖线与竖线间的误差
    #set_deviation_y() can change the value of DEVIATION_BETWEEN_Y
    rails_on_x = machine_classify_crossing_x( DEVIATION_BETWEEN_Y )
    #adjust the crossing_x
    for rail in rails_on_x:
        if len(rail)>2:
            bb=rail[0]
            for i in range(len(rail)-1):
                kk=abs(rail[i+1])-1 #give back for before
                if rail[i+1]>0: #up and down
                    rectangle_list[kk]=co.adjust(angle+90,bb,rectangle_list[kk],3)#left 0 1
                else:
                    rectangle_list[kk]=co.adjust(angle+90,bb,rectangle_list[kk],4)#right 2 3

    return rectangle_list


#expand
def expand(img, color, step=3):
    '''将图像的一种颜色进行膨胀扩张step个像素点【临时函数，将来可能会删除】'''
    if color == "black":c1,c2 = 255, 0
    else:c1,c2 =0, 255
    img_paper = create_paper(img.shape, c1)
    for i in range(len(img))[step:-step]:
        for j in range(len(img[i]))[step:-step]:
            if img[i][j] == c2:
                for ii in range(i+1+step)[i-step:]:
                    for jj in range(j+1+step)[j-step:]:
                        img_paper[ii][jj] = c2
    return img_paper



#input angle<"float">
#input rectangle_list<"list> [rect1, rect2 ...]
#input img1<"numpy.ndarray">
def draw_test(angle, rectangle_list, img1):
    '''画出识别的结果，测试之用【临时函数，将来可能会删除】'''
    
    def tutu(p):
        return (p[0],p[1])

    def intu(p):
        return((int(round(p[0])),int(round(p[1]))))

    stepW=10 #xianju chuizhipingyi
    #fourth time round all the rects to draw
    
    for kk in range(len(rectangle_list)):
        points = np.int0(np.around(rectangle_list[kk])) #int(four points of rect)
        cv2.polylines(img1,[points],True,(255,255,255),2) #draw rects
        if co.dis_lianbiao(points[0],points[1])<co.dis_lianbiao(points[2],points[1]):
            #heng
            cv2.line(img1,co.cenint(points[0],points[1]),co.cenint(points[2],points[3]),(255,255,255),1)
            pp1=co.cen(points[0],points[1])
            pp2=tutu(points[1])
            while pp2[0]+stepW*math.cos(math.radians(angle))<points[2][0]:
                pp1,pp2=co.right_copy(pp1,pp2,stepW,angle)
                cv2.line(img1,intu(pp1),intu(pp2),(255,255,255),1)
        else:
            #zong
            cv2.line(img1,co.cenint(points[2],points[1]),co.cenint(points[0],points[3]),(255,255,255),1)
            pp1=co.cen(points[2],points[1])
            pp2=tutu(points[1])
            while pp2[1]+stepW*math.sin(math.radians(angle)+90)<points[0][1]:
                pp1,pp2=co.right1_copy(pp1,pp2,stepW,angle)
                cv2.line(img1,intu(pp1),intu(pp2),(255,255,255),1)


###Begin the main project###
###Just have a test###
if __name__ == "__main__":
    img = open_image('./t1.jpg')
    img_black_paper = create_paper(img.shape)
    #img_threshold = get_black_and_white_image(img, 200) #发现没有必要二值化处理
    img_gray = get_gray_image(img)
    img_close = close_gap(img_gray, 3)
  
    set_deviation_x(4)
    set_deviation_y(4)
    contours = get_contour_cornerlists(img_close, img)

    rectangles = []
    for contour in contours:
        rectangles.append( get_rectangle(contour) )

    #angle adjust
    rectangles = machine_classify( rectangles )

    #get the side_point_adjusted four_point_rect
    rectangles_four_points = machine_optimize( rectangles )
    print rectangles_four_points

    for i in xrange(len(rectangles)):
        draw_test(rectangles[i][0][2], rectangles_four_points[i], img_black_paper)

    save_image('result.jpg',img_black_paper)

    cv2.namedWindow('img_close')
    cv2.imshow('img',img_close)
    cv2.namedWindow('img_result')
    cv2.imshow('img_result',img_black_paper)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
