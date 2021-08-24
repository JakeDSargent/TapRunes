#!/usr/bin/env python

from math import pi, sin, cos
import cairo
import character_writer as CW
import random
import os
import csv

class SigilWriter:
  GLYPH_WIDTH, GLYPH_HEIGHT = 500, 500
  LINE_WIDTH = GLYPH_WIDTH // 50
  XPAD, YPAD = LINE_WIDTH * 2, LINE_WIDTH * 4

  def __init__(self,
               scale,
               char_width=1,
               char_height=1,
               ctx=None,
               surface=None,
               palette=None):

    if palette is not None:
      self.palette = palette
    else:
      self.palette = [(1, 0, 0),
                      (0, 1, 0),
                      (0, 0, 1)]

    self.process_scale(scale)
    self.cursor_x = self.XPAD + self.LINE_WIDTH + self.x_scaled / 2
    self.cursor_y = self.YPAD + self.LINE_WIDTH + self.y_scaled / 2
    self.x_home = self.cursor_x
    self.y_home = self.cursor_y
    if ctx is not None and surface is not None:
      self.ctx = ctx
      self.surface = surface
      self.ctx.set_line_width(self.LINE_WIDTH)
      self.ctx.set_line_join(cairo.LINE_JOIN_ROUND)
      self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)
      self.ctx.save()
      self.writer_scale = scale / 1.5
      self.writer = CW.CharacterWriter(scale / 1.5, ctx=self.ctx, surface=self.surface)
      self.ctx.restore()
    else:
      self.generate_default_context()

    self.big_r = .1
    self.small_r = .08

    self.coords = {
      "LEVEL":    (0,0),
      "C/R":      (0,0),
      "CASTINGTIME":     (0,0),
      "DURATION": (0,0),
      "TARGET":   (0,0),
      "SCHOOL":   (0,0),
      "DAMAGE":   (0,0),
      "RANGE":    (0,0)
    }
    self.draw_type = {
      "NOSAVE":  self.no_save,
      "ATTACK":  self.attack,
      "STR"   :  self.str_save,
      "DEX"   :  self.dex_save,
      "CON"   :  self.con_save,
      "INT"   :  self.int_save,
      "WIS"   :  self.wis_save,
      "CHA"   :  self.cha_save
    }

  def generate_default_context(self):
    self.pixel_width = int((self.x_scaled + self.XPAD * 2) + 2 * self.LINE_WIDTH)
    self.pixel_height = int((self.y_scaled + self.YPAD * 2) + 2 * self.LINE_WIDTH)
    self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.pixel_width,
                                      self.pixel_height)
    ctx = cairo.Context(self.surface)
    ctx.set_source_rgb(0, 0, 0)
    ctx.rectangle(0, 0, self.pixel_width, self.pixel_height)
    ctx.fill()
    pat = cairo.RadialGradient(self.cursor_x, self.cursor_y, 0.0, self.cursor_x, self.cursor_y, max(self.pixel_width, self.pixel_height)/2)
    # add_color_stop_rbga(offset, % red, % green, % blue, % opacity)
    num_stops = len(self.palette)*2
    for i in range(num_stops):
      r, g, b = self.palette[i%len(self.palette)]
      pat.add_color_stop_rgb(1/num_stops * i, r, g, b)

    ctx.set_source(pat)
    self.ctx = ctx

    self.ctx.set_line_width(self.LINE_WIDTH)
    self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    self.ctx.save()
    self.writer_scale = self.scale / 1.5
    self.writer = CW.CharacterWriter(self.scale / 1.5, ctx=self.ctx, surface=self.surface)
    self.ctx.restore()

  def export_image(self, filename="example.png"):
    self.surface.write_to_png(filename)  # Output to PNG

  def process_scale(self, scale):
    self.scale = scale
    self.x_scaled = self.GLYPH_WIDTH * scale
    self.y_scaled = self.GLYPH_HEIGHT * scale
    self.XPAD *= scale
    self.YPAD *= scale
    self.LINE_WIDTH *= scale

  def hex_to_rgb(self, hex_color_str):
    if len(hex_color_str) == 7 and hex_color_str[0] == "#":
      hex_color_str = hex_color_str[1:]
    if len(hex_color_str) == 6:
      r = int(hex_color_str[:2], 16)/255.0
      g = int(hex_color_str[2:4], 16)/255.0
      b = int(hex_color_str[4:], 16)/255.0
    else:
      return False
    return (r,g,b)

  def rel_to_user_x(self, rel_x):
    return rel_x * self.x_scaled + self.cursor_x

  def rel_to_user_y(self, rel_y):
    return rel_y * self.y_scaled + self.cursor_y

  def x_y_from_angle(self, angle, radius):
    angle = angle % (2*pi)
    x = cos(angle) * radius
    y = sin(angle) * radius

    return x, y

  def place_cursor(self, x, y):
    self.x_home = x
    self.y_home = y

  def stroke(self):
    self.ctx.stroke()

  def fill(self):
    self.ctx.fill()

  def init_cursor(self, rel_x=0, rel_y=0):
    self.ctx.new_path()
    self.move_to(rel_x, rel_y)

  def arc(self, rel_x, rel_y, rad, angle_1, angle_2, fill=False):
    self.ctx.save()
    self.ctx.new_sub_path()
    self.ctx.translate(self.cursor_x, self.cursor_y)
    self.ctx.scale(self.x_scaled, self.y_scaled)
    self.ctx.set_line_width(self.LINE_WIDTH / self.x_scaled * 0.75)
    self.ctx.arc(rel_x, rel_y, rad, angle_1, angle_2)
    if fill:
      self.fill()
    else:
      self.stroke()
    self.ctx.restore()

  def overwriting_arc(self, rel_x, rel_y, rad, angle_1, angle_2):
    self.ctx.save()
    self.ctx.set_source_rgb(0, 0, 0)
    self.arc(rel_x, rel_y, rad, 0, 2*pi, fill=True)
    self.ctx.restore()
    self.arc(rel_x, rel_y, rad, 0, 2*pi) 

  def move_to(self, rel_x, rel_y):
    self.ctx.move_to(self.rel_to_user_x(rel_x), self.rel_to_user_y(rel_y))

  def rel_move(self, dx, dy):
    self.ctx.rel_move_to(dx * self.x_scaled, dy * self.y_scaled)

  def line_to(self, rel_x, rel_y):
    self.ctx.line_to(self.rel_to_user_x(rel_x), self.rel_to_user_y(rel_y))

  def line(self, rel_x1, rel_y1, rel_x2, rel_y2):
    self.move_to(rel_x1, rel_y1)
    self.line_to(rel_x2, rel_y2)

  def curve_to(self, x1, y1, x2, y2, x3, y3):
    self.ctx.curve_to(self.rel_to_user_x(x1), self.rel_to_user_y(y1),
                      self.rel_to_user_x(x2), self.rel_to_user_y(y2),
                      self.rel_to_user_x(x3), self.rel_to_user_y(y3))

  def draw_nothing(self):
    pass

  def find_key_coords(self, rad3, rad5, equidistant=False):
    inc3 = 2*pi/3
    base3 = pi*3/2
    
    inc5 = 2*pi/5
    base5 = pi/2 - 2*inc5

    base8=base3
    inc8 = 2*pi/8
    if not equidistant:
      self.coords["LEVEL"]    = self.x_y_from_angle(base3 + inc3 * 0, rad3)
      self.coords["C/R"]      = self.x_y_from_angle(base3 + inc3 * 1, rad3)
      self.coords["CASTINGTIME"]     = self.x_y_from_angle(base3 + inc3 * 2, rad3)
      self.coords["DURATION"] = self.x_y_from_angle(base5 + inc5 * 0, rad5)
      self.coords["TARGET"]   = self.x_y_from_angle(base5 + inc5 * 1, rad5)
      self.coords["SCHOOL"]   = self.x_y_from_angle(base5 + inc5 * 2, rad5)
      self.coords["DAMAGE"]   = self.x_y_from_angle(base5 + inc5 * 3, rad5)
      self.coords["RANGE"]    = self.x_y_from_angle(base5 + inc5 * 4, rad5)
    else:
      self.coords["LEVEL"]    = self.x_y_from_angle(base8 + inc8 * 0, rad3)
      self.coords["DURATION"] = self.x_y_from_angle(base8 + inc8 * 1, rad5)
      self.coords["TARGET"]   = self.x_y_from_angle(base8 + inc8 * 2, rad5)
      self.coords["C/R"]      = self.x_y_from_angle(base8 + inc8 * 3, rad3)
      self.coords["SCHOOL"]   = self.x_y_from_angle(base8 + inc8 * 4, rad5)
      self.coords["CASTINGTIME"]     = self.x_y_from_angle(base8 + inc8 * 5, rad3)
      self.coords["DAMAGE"]   = self.x_y_from_angle(base8 + inc8 * 6, rad5)
      self.coords["RANGE"]    = self.x_y_from_angle(base8 + inc8 * 7, rad5)

  def draw_sigil_circles(self):
    self.LINE_WIDTH /= 2
    self.ctx.set_line_width(self.LINE_WIDTH)
    count = 0
    for key in self.coords:
      x, y = self.coords[key]
      if count < 3:
        self.overwriting_arc(x, y, self.big_r, 0, 2*pi)
      else:
        self.overwriting_arc(x, y, self.small_r, 0, 2*pi)
      count += 1
    self.LINE_WIDTH *= 2
    self.ctx.set_line_width(self.LINE_WIDTH)

  def no_save(self):
    self.init_cursor()
    rad3, rad5 = .125, .4
    self.find_key_coords(rad3, rad5)
    keys = list(self.coords.keys())
    self.use_random_gradient()
    self.arc(0, 0, rad5, 0, 2 * pi)
    self.use_random_gradient()
    for i in range(5):
      x1, y1 = self.coords[keys[(i%5)+3]]
      x2, y2 = self.coords[keys[((i+1)%5)+3]]
      self.line(x1, y1, x2, y2)
      self.stroke()
    self.use_random_gradient()
    self.arc(0, 0, rad3 + (rad5-rad3)/2, 0, 2*pi)
    self.use_random_gradient()
    

    self.draw_sigil_circles()
    
  def cha_save(self):
    self.init_cursor()

    rad3, rad5 = .175, .45
    self.find_key_coords(rad3, rad5)
    keys = list(self.coords.keys())
    self.use_random_gradient()
    for i in range(5):
      x1, y1 = self.coords[keys[(i%5)+3]]
      for j in range(1, 5-i):
        x2, y2 = self.coords[keys[((i+j)%5)+3]]
        self.line(x1, y1, x2, y2)
    self.stroke()
    self.use_random_gradient()
    self.arc(0, 0, rad3 + (rad5-rad3)/2, 0, 2*pi)
    self.use_random_gradient()
    self.draw_sigil_circles()

  def attack(self):
    self.init_cursor()

    rad3, rad5 = .4, .25
    self.find_key_coords(rad3, rad5, equidistant=True)
    keys = list(self.coords.keys())

    for i in range(8):
      self.use_random_gradient()
      x1, y1 = self.coords[keys[i]]
      self.line(0,0,x1,y1)
      self.stroke()
    self.use_random_gradient()
    self.draw_sigil_circles()

  def wis_save(self):
    self.init_cursor()

    rad3, rad5 = .15, .4
    self.find_key_coords(rad3, rad5)
    for i in range(5):
      inc5 = 2*pi/5
      base5 = pi/2 - 2*inc5
      x,y = self.x_y_from_angle(base5+inc5*i, .55)
      self.use_random_gradient()
      self.line(0,0,x,y)
      self.stroke()
    self.use_random_gradient()
    self.overwriting_arc(0,0,rad3,0,2*pi)
    self.use_random_gradient()
    self.arc(0,0,rad5-self.small_r,0,2*pi)
    self.use_random_gradient()
    self.draw_sigil_circles()

  def str_save(self):
    self.init_cursor()

    rad3, rad5 = .175, .4
    self.find_key_coords(rad3, rad5)
    keys = list(self.coords.keys())
    self.use_random_gradient()
    self.arc(0,0,rad3,0,2*pi)
    self.use_random_gradient()
    for i in range(3):
      x1, y1 = self.coords[keys[(i%3)]]
      x2, y2 = self.coords[keys[((i+1)%3)]]
      self.line(x1, y1, x2, y2)
      self.stroke()
    self.use_random_gradient()
    for i in range(5):
      x1, y1 = self.coords[keys[(i%5)+3]]
      x2, y2 = self.coords[keys[((i+1)%5)+3]]
      self.line(x1, y1, x2, y2)
      self.stroke()
    self.use_random_gradient()
    self.draw_sigil_circles()

  def dex_save(self):
    self.init_cursor()
    self.use_random_gradient()
    rad3, rad5 = .42, .16
    self.find_key_coords(rad3, rad5)
    for i in range(3):
      inc3 = 2*pi/3
      base3 = 3*pi/2
      x,y = self.x_y_from_angle(base3+inc3*i, .55)
      self.line(0,0,x,y)
      self.stroke()
    self.use_random_gradient()
    self.overwriting_arc(0,0,rad5,0,2*pi)
    self.use_random_gradient()
    self.arc(0, 0, rad5 + (rad3-rad5)/2, 0, 2*pi)
    self.use_random_gradient()
    self.draw_sigil_circles()

  def int_save(self):
    self.init_cursor()

    rad3, rad5 = .175, .4
    self.find_key_coords(rad3, rad5)
    keys = list(self.coords.keys())
    self.use_random_gradient()
    self.arc(0,0,rad5,0,2*pi)
    self.use_random_gradient()
    for i in range(3):
      x1, y1 = self.coords[keys[(i%3)]]
      self.line(x1, y1, 0, 0)
      self.stroke()
    self.use_random_gradient()
    self.draw_sigil_circles()

  def con_save(self):
    self.init_cursor()

    rad3, rad5 = .4, .175
    self.find_key_coords(rad3, rad5)
    keys = list(self.coords.keys())
    self.use_random_gradient()
    self.arc(0,0,rad3,0,2*pi)
    self.use_random_gradient()
    for i in range(5):
      x1, y1 = self.coords[keys[(i%5)+3]]
      self.line(x1, y1, 0, 0)
      self.stroke()
    self.use_random_gradient()
    self.draw_sigil_circles()

  def draw_school_sigil(self, school):
    x, y = self.coords["SCHOOL"]
    if school == "CONJURATION":
      self.arc(x, y+self.small_r/2, self.small_r/2, pi, 2*pi)
      self.line(x, y - self.small_r/4, x, y-3*self.small_r/4)
      self.line(x + self.small_r * 3/8, y - self.small_r/4, x + self.small_r * 5/8, y - self.small_r/2)
      self.line(x - self.small_r * 3/8, y - self.small_r/4, x - self.small_r * 5/8, y - self.small_r/2)
      self.stroke()
    elif school == "NECROMANCY":
      offset = self.small_r/8
      self.arc(x, y - offset, 5*offset, 3*pi/4, 9*pi/4)
      line_off_x, line_off_y = self.x_y_from_angle(3*pi/4, 5*offset)
      self.move_to(x + line_off_x, y - offset + line_off_y)
      self.line_to(x + line_off_x, y + 2*offset + line_off_y)
      self.line_to(x - line_off_x, y + 2*offset + line_off_y)
      self.line_to(x - line_off_x, y - offset + line_off_y)
      self.line(x + line_off_x + offset, y + line_off_y + offset/2, x - line_off_x - offset, y + line_off_y + offset/2)
      self.line(x, y + offset, x + offset/2, y + 2*offset)
      self.line(x, y + offset, x - offset/2, y + 2*offset)
      self.arc(x + line_off_x/2, y - offset, offset, 0, 2*pi)
      self.arc(x - line_off_x/2, y - offset, offset, 0, 2*pi)
      self.stroke()
    elif school == "EVOCATION":
      self.arc(x, y, self.small_r/8, 0, 2*pi)
      self.line(x, y - self.small_r * 3/8, x, y-3*self.small_r/4)
      self.line(x + self.small_r * 3/8, y - self.small_r/4, x + self.small_r * 5/8, y - self.small_r/2)
      self.line(x - self.small_r * 3/8, y - self.small_r/4, x - self.small_r * 5/8, y - self.small_r/2)

      self.line(x, y + self.small_r * 3/8, x, y + self.small_r * 3/4)
      self.line(x + self.small_r * 3/8, y + self.small_r/4, x + self.small_r * 5/8, y + self.small_r/2)
      self.line(x - self.small_r * 3/8, y + self.small_r/4, x - self.small_r * 5/8, y + self.small_r/2)
      self.stroke()
    elif school == "ABJURATION":
      vert_offset = self.small_r*2/3
      horiz_offset = self.small_r/2
      self.line(x + horiz_offset, y-vert_offset, x-horiz_offset, y-vert_offset)
      self.line_to(x-horiz_offset, y+vert_offset/2)
      self.line_to(x, y+vert_offset)
      self.line_to(x + horiz_offset, y + vert_offset/2)
      self.line_to(x + horiz_offset, y-vert_offset)
      self.line(x, y-vert_offset, x, y+vert_offset)
      self.line(x+horiz_offset, y-vert_offset/4, x, y)
      self.line(x-horiz_offset, y-vert_offset/4, x, y)
      self.stroke()
    elif school == "TRANSMUTATION":
      horiz_offset = self.small_r/3
      self.arc(x - horiz_offset, y, self.small_r/2, pi/4, pi*7/4, fill=True)
      self.arc(x + horiz_offset, y, self.small_r/2, pi*5/4, pi*11/4, fill=True)
    elif school == "DIVINATION":
      self.arc(x, y-self.small_r/2, self.small_r/2, 0, pi)
      self.line(x, y + self.small_r * 1/4, x, y + self.small_r * 3/4)
      self.line(x + self.small_r * 3/8, y + self.small_r/4, x + self.small_r * 5/8, y + self.small_r/2)
      self.line(x - self.small_r * 3/8, y + self.small_r/4, x - self.small_r * 5/8, y + self.small_r/2)
      self.stroke()
    elif school == "ENCHANTMENT":
      pitch = 8
      for i in range(1, pitch):
        if (i % 2 == 1):
          self.arc(x + self.small_r/(pitch), y, i * self.small_r/pitch, pi, 2*pi)
        else:
          self.arc(x, y, i*self.small_r/pitch, 0, pi)
    elif school == "ILLUSION":
      self.ctx.save()
      eye_rad = self.small_r/3
      vert_offset = self.small_r/6
      self.arc(x, y, eye_rad, pi, 2*pi)
      self.line(x-eye_rad, y, x-2*eye_rad, y)
      self.line(x+eye_rad, y, x+2*eye_rad, y)
      self.arc(x, y+vert_offset*2, eye_rad, 0, pi)
      self.line(x-eye_rad, y+vert_offset*2, x-2*eye_rad, y+vert_offset*2)
      self.line(x+eye_rad, y+vert_offset*2, x+2*eye_rad, y+vert_offset*2)
      self.arc(x, y+vert_offset, eye_rad/2, 0, 2*pi)

      self.line(x, y - eye_rad, x, y-3*self.small_r/4)
      self.line(x + self.small_r * 3/8, y - self.small_r/4, x + self.small_r * 5/8, y - self.small_r/2)
      self.line(x - self.small_r * 3/8, y - self.small_r/4, x - self.small_r * 5/8, y - self.small_r/2)
      self.stroke()
    
  def draw_CR_sigil(self, C=False, R=False):
    self.ctx.save()
    self.use_random_gradient()
    self.ctx.set_line_width(int(self.LINE_WIDTH // 10) | 1)
    x, y = self.coords["C/R"]
    self.ctx.new_sub_path()
    self.ctx.translate(self.cursor_x, self.cursor_y)
    self.ctx.scale(self.x_scaled, self.y_scaled)
    self.ctx.set_line_width(self.LINE_WIDTH / self.x_scaled * 0.75)
    self.ctx.arc(x, y, self.big_r, -pi/2, pi/2)
    self.ctx.restore()
    self.ctx.save()
    self.ctx.set_line_width(int(self.LINE_WIDTH // 10) | 1)
    r,g,b = random.choice(self.palette)
    self.ctx.set_source_rgb(r, g, b)
    offset = self.big_r/2
    self.curve_to(x + 2*offset, y + offset, x - 2*offset, y - offset, x, y - self.big_r)
    if R:
      self.fill()
    else:
      self.stroke()
    self.ctx.restore()

    self.ctx.save()
    self.use_random_gradient()
    self.ctx.set_line_width(int(self.LINE_WIDTH // 10) | 1)
    self.ctx.new_sub_path()
    self.ctx.translate(self.cursor_x, self.cursor_y)
    self.ctx.scale(self.x_scaled, self.y_scaled)
    self.ctx.set_line_width(self.LINE_WIDTH / self.x_scaled * 0.75)
    self.ctx.arc_negative(x, y, self.big_r, -pi/2, pi/2)
    self.ctx.restore()
    self.ctx.save()
    self.ctx.set_line_width(int(self.LINE_WIDTH // 10) | 1)
    r,g,b = random.choice(self.palette)
    self.ctx.set_source_rgb(r, g, b)
    offset = self.big_r/2
    self.curve_to(x + 2*offset, y + offset, x - 2*offset, y - offset, x, y - self.big_r)
    if C:
      self.fill()
    else:
      self.stroke()
    self.ctx.restore()
  
  def write_name(self, name):
    x_pos = int(self.writer.x_scaled + self.writer.XPAD)
    self.writer.place_cursor(x_pos, 0)
    self.draw_sigil("NAME", name)

  def draw_shape(self, key, shape):
    x, y = self.coords[key]

    if shape in ["SQUARE", "D6"]:
      x_off, y_off = self.x_y_from_angle(pi/4, self.small_r)
      x_off -= self.small_r/10
      y_off -= self.small_r/10
      self.line(x+x_off, y+y_off, x-x_off, y+y_off)
      self.line_to(x-x_off, y-y_off)
      self.line_to(x+x_off, y-y_off)
      self.line_to(x+x_off, y+y_off)
      self.stroke()
    elif shape == "CIRCLE":
      rad = self.small_r * 5/7
      self.arc(x,y,rad,0,2*pi) 
    elif shape == "CONE":
      x_base, y_base = self.x_y_from_angle(pi/2, self.small_r)
      x_left, y_left = self.x_y_from_angle(5*pi/4, self.small_r)
      x_right, y_right = self.x_y_from_angle(7*pi/4, self.small_r)
      self.line(x + x_base, y + y_base, x + x_left, y + y_left)
      self.line(x + x_base, y + y_base, x + x_right, y + y_right)
      self.stroke()
    elif shape == "SELF":
      self.move_to(x, y-self.small_r/3)
      self.curve_to(x+self.small_r/3, y-self.small_r*1.25, x+self.small_r*1.5, y, x, y+self.small_r*0.8) 
      self.move_to(x, y-self.small_r/3)
      self.curve_to(x-self.small_r/3, y-self.small_r*1.25, x-self.small_r*1.5, y, x, y+self.small_r*0.8) 
      self.stroke()
    elif shape == "CREATURE":
      self.move_to(x, y+self.small_r/3)
      self.curve_to(x+self.small_r/3, y+self.small_r*1.25, x+self.small_r*1.5, y, x, y-self.small_r*0.8) 
      self.move_to(x, y+self.small_r/3)
      self.curve_to(x-self.small_r/3, y+self.small_r*1.25, x-self.small_r*1.5, y, x, y-self.small_r*0.8) 
      self.stroke() 
    elif shape == "D4":
      offset = self.small_r/10
      x1, y1 = self.x_y_from_angle(pi/6, self.small_r)
      x2, y2 = self.x_y_from_angle(5*pi/6, self.small_r)
      self.line(x, y-self.small_r + offset, x+x1-offset, y+y1-offset)
      self.line_to(x+x2+offset, y+y2-offset)
      self.line_to(x, y-self.small_r + offset)
      self.stroke()
    elif shape == "D8":
      offset = self.small_r*9/10
      self.line(x, y - offset, x + offset, y)
      self.line_to(x, y + offset)
      self.line_to(x - offset, y)
      self.line_to(x, y - offset)  
      self.stroke()
    elif shape == "D10":
      offset = self.small_r/10
      x1, y1 = self.x_y_from_angle(pi/6, self.small_r)
      x2, y2 = self.x_y_from_angle(5*pi/6, self.small_r)
      self.line(x, y-self.small_r + offset, x+x1-offset, y+y1-offset)
      self.line_to(x,y+self.small_r - offset)
      self.line_to(x+x2+offset, y+y2-offset)
      self.line_to(x, y-self.small_r + offset)
      self.stroke() 
    elif shape == "D12":
      rad = self.small_r*0.8
      inc = 2 * pi / 5
      start = pi/2
      for i in range(1, 6):
        if (i == 1):
          xo, yo = self.x_y_from_angle(start, rad)
          self.move_to(x+xo, y+yo)
        xo, yo = self.x_y_from_angle(start + inc*i, rad)
        self.line_to(x+xo, y+yo)
      self.stroke()

  def draw_components(self, vsm):
    rad = 2*self.big_r - self.small_r
    if "M" in vsm:
      x,y = self.coords["LEVEL"]
      self.arc(x,y,rad,0, 2*pi)
    if "S" in vsm:
      x,y = self.coords["C/R"]
      self.arc(x,y,rad,0, 2*pi)
    if "V" in vsm:
      x,y = self.coords["CASTINGTIME"]
      self.arc(x,y,rad,0, 2*pi)


  def draw_sigil(self, key, sigils):
    name = key == "NAME"
    self.ctx.save()    
    insc = self.writer.parse_inscription(sigils.strip("\n"))
    self.ctx.set_source_rgb(249/255, 190/255, 25/255)
    if not name:
      x,y = self.coords[key]
      scale_shift = 1 - (0.15 * (len(insc) - 1))
      if key in ["LEVEL", "C/R", "CASTINGTIME"]:
        scale_shift *= self.big_r / self.small_r
    else:
      scale_shift=0.5
    self.writer.process_scale(scale_shift)
    self.ctx.set_line_width(self.writer.LINE_WIDTH)
    if len(insc) > 1:
      x_offset = (self.writer.x_scaled + self.writer.XPAD) / 2 * (len(insc)-1)
    else:
      x_offset = 0
    y_offset = self.writer.y_scaled / 2
    if not name:
      self.writer.place_cursor(self.rel_to_user_x(x) - x_offset, self.rel_to_user_y(y) - y_offset)
    self.writer.write_inscription(insc)
    self.writer.process_scale(1 / scale_shift)
    self.ctx.restore()

  def use_random_gradient(self, num_stops=10, radial=True):
    if radial:
      pat = cairo.RadialGradient(self.cursor_x, self.cursor_y, 0.0, self.cursor_x, self.cursor_y, max(self.pixel_width, self.pixel_height)/2)
    else:
      x,y = random.choice([(0,self.pixel_height), 
                           (self.pixel_width, self.pixel_height),
                           (self.pixel_width, 0)])
      pat = cairo.LinearGradient(0.0, 0.0, x, y)

    for i in range(num_stops):
      r, g, b = random.choice(self.palette)
      pat.add_color_stop_rgb(1/num_stops * i, r, g, b)

    self.ctx.set_source(pat)
  
  def use_random_solid_color(self):
    r,g,b = random.choice(self.palette)
    self.ctx.set_source_rgb(r,g,b)

  def load_palette(self, palette_str, overwrite=True):
    palette = [] if overwrite else self.palette
    for color in palette_str.split("#"):
      color = self.hex_to_rgb(color)
      if color:
        palette.append(color)
    self.palette = palette
  
  def draw_spell_from_dict(self, spell_dict):
    if "PALETTE" in spell_dict:
      self.load_palette(spell_dict["PALETTE"])
    self.write_name(spell_dict["NAME"])
    self.use_random_gradient()
    self.draw_type[spell_dict["SAVE"]]()
    self.LINE_WIDTH /= 2
    self.ctx.set_line_width(self.LINE_WIDTH)
    if "TARGETSHAPE" in spell_dict:
      self.use_random_gradient(radial=False)
      self.draw_shape("TARGET", spell_dict["TARGETSHAPE"])
    if "DAMAGEDICE" in spell_dict:
      self.use_random_gradient(radial=False)
      self.draw_shape("DAMAGE", spell_dict["DAMAGEDICE"])
    for key in ["LEVEL", "RANGE", "DAMAGE", "CASTINGTIME", "DURATION", "TARGET"]:
      self.draw_sigil(key, spell_dict[key])
    c = "C" in spell_dict["C/R"]
    r = "R" in spell_dict["C/R"]
    self.draw_CR_sigil(C=c, R=r)
    self.use_random_gradient(radial=False)
    self.draw_school_sigil(spell_dict["SCHOOL"])
    
    self.use_random_gradient()
    self.draw_components(spell_dict["COMPONENTS"])

  def parse_dir(self, indir="src", outdir="out"):
    for filename in os.scandir(indir):
      if filename.is_file() and filename.name.endswith(".spl"):
        outname = filename.name.split('.')[0] + ".png"
        name = " ".join(filename.name.split('.')[0].split("_"))
        print(name)
        spell_dict = {}
        spell_dict["NAME"] = name
        with open(filename.path, "r") as infile:
          parser = csv.reader(infile, delimiter=":")
          for row in parser:
            if len(row) == 2:
              spell_dict[row[0]] = row[1]
        self.draw_spell_from_dict(spell_dict)
        self.export_image(outdir + "/" +spell_dict["LEVEL"] + "_" + outname)
        self.LINE_WIDTH *= 2
        self.ctx.set_line_width(self.LINE_WIDTH)
        self.generate_default_context()
    

def main():

  scribe = SigilWriter(2)
  scribe.parse_dir()
  #scribe.parse_dir(indir="test", outdir="test")
  
  # scribe.draw_type["CON"]()
  # scribe.draw_sigil("LEVEL", ["2"])
  # scribe.draw_sigil("RANGE", ["60"])
  # scribe.draw_sigil("DAMAGE", [" ","0"," "])
  # scribe.draw_sigil("CASTINGTIME", ["*"])
  # scribe.draw_sigil("DURATION", ["1", "M"])
  # scribe.draw_CR_sigil(C="True")
  # scribe.draw_school_sigil("ENCHANTMENT")
  # scribe.draw_shape("TARGET", "CIRCLE")
  # scribe.draw_sigil("TARGET", ["20"])
  # scribe.draw_components("VS")

  
  # scribe.export_image("spell_card" + ".png")


if __name__ == "__main__":
  main()
