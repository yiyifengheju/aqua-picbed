from PIL import Image, ImageDraw, ImageFilter

# 创建空白图层A
width = 400  # 图层A的宽度
height = 400  # 图层A的高度
image_A = Image.new('RGBA', (width, height), (255, 255, 255, 255))  # 白色背景

# 添加阴影效果
shadow_color = (0, 0, 0, 128)  # 阴影颜色，半透明黑色
shadow_offset = (50, 50)  # 阴影偏移量
shadow_blur_radius = 200  # 阴影模糊半径

# 创建绘图对象
draw = ImageDraw.Draw(image_A)

# 绘制阴影
draw.rectangle([(shadow_offset[0], shadow_offset[1]), (width - shadow_offset[0], height - shadow_offset[1])], fill=shadow_color)

# 对阴影进行模糊处理
blurred_shadow = image_A.filter(ImageFilter.GaussianBlur(shadow_blur_radius))

# 将模糊处理后的阴影叠加到图层A上
image_A = Image.alpha_composite(image_A, blurred_shadow)

# 显示或保存图层A
image_A.show()
# image_A.save("layer_A_with_box_shadow.png")