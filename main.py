#!/usr/bin/env python

import math
import cairo

class CharacterWriter:
  CHAR_WIDTH, CHAR_HEIGHT = 50, 80
  LINE_WIDTH = 5
  XPAD, YPAD = LINE_WIDTH *2, LINE_WIDTH *2

  def __init__(self, scale, char_width=1, char_height=1, ctx=None, surface=None):
    self.process_scale(scale)
    self.cursor_x = self.XPAD + self.x_scaled / 2
    self.cursor_y = self.YPAD
    self.x_home = self.cursor_x
    self.y_home = self.cursor_y
    if ctx is not None and surface is not None:
      self.ctx = ctx  
      self.surface = surface
    else:
      self.generate_default_context(char_width, char_height)
    self.ctx.set_line_width(self.LINE_WIDTH)

    self.runes = {"A": self.A,
                  "B": self.B,
                  "C": self.C,
                  "D": self.D,
                  "E": self.E,
                  "F": self.F,
                  "G": self.G,
                  "H": self.H,
                  "I": self.I,
                  "J": self.J,
                  "K": self.K,
                  "L": self.L,
                  "M": self.M,
                  "N": self.N,
                  "O": self.O,
                  "P": self.P,
                  "Q": self.Q,
                  "R": self.R,
                  "S": self.S,
                  "T": self.T,
                  "U": self.U,
                  "V": self.V,
                  "W": self.W,
                  "X": self.X,
                  "Y": self.Y,
                  "Z": self.Z,
                  " ": self.advance_cursor,
                  }
  
  def generate_default_context(self, char_width, char_height):
    pixel_width = int(char_width * (self.CHAR_WIDTH + 2.5 * self.XPAD))
    pixel_height = int(char_height * (self.CHAR_HEIGHT + 2.5 * self.YPAD))
    self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixel_width, pixel_height)
    ctx = cairo.Context(self.surface)

    pat = cairo.LinearGradient(0.0, 0.0, 0.0, pixel_height)
    pat.add_color_stop_rgba(1, 0.7, 0, 0, 0.5)  # First stop, 50% opacity
    pat.add_color_stop_rgba(0, 0.9, 0.7, 0.2, 1)  # Last stop, 100% opacity

    ctx.set_source(pat)
    self.ctx = ctx    

  def export_image(self, filename="example.png"):
    self.surface.write_to_png(filename)  # Output to PNG

  def process_scale(self, scale):
    self.scale = scale
    self.x_scaled = self.CHAR_WIDTH * scale
    self.y_scaled = self.CHAR_HEIGHT * scale
    self.XPAD *= scale 
    self.YPAD *= scale 
    self.LINE_WIDTH *= scale

  def rel_to_user_x(self, rel_x):
    return rel_x * self.x_scaled + self.cursor_x

  def rel_to_user_y(self, rel_y):
    return rel_y * self.y_scaled + self.cursor_y

  def advance_cursor(self):
    self.cursor_x += self.XPAD + self.x_scaled

  def line_feed(self):
    self.cursor_y += self.YPAD + self.y_scaled

  def carriage_return(self):
    self.cursor_x = self.x_home

  def newline(self):
    self.line_feed()
    self.carriage_return()

  def line_return(self):
    self.cursor_y = self.y_home

  def place_cursor(self, x, y):
    self.x_home = x
    self.y_home = y
    self.carriage_return()
    self.line_return()

  def stroke(self):
    self.ctx.stroke()

  def init_char(self, rel_x=0, rel_y=0):
    self.ctx.new_path()
    self.move_to(rel_x, rel_y)

  def vert(self, len):
    self.ctx.rel_line_to(0, len * self.y_scaled)

  def v_to_bottom(self):
    x, y = self.ctx.get_current_point()
    self.ctx.line_to(self.rel_to_user_x(-0.5), self.rel_to_user_y(1))
    self.ctx.move_to(x, y)
    self.ctx.line_to(self.rel_to_user_x(0.5), self.rel_to_user_y(1))
    self.ctx.move_to(x, y)

  def v_to_top(self):
    x, y = self.ctx.get_current_point()
    self.ctx.line_to(self.rel_to_user_x(-0.5), self.cursor_y)
    self.ctx.move_to(x, y)
    self.ctx.line_to(self.rel_to_user_x(0.5), self.cursor_y)
    self.ctx.move_to(x, y)

  def flag_left(self, end_y):
    x, y = self.ctx.get_current_point()
    left_x = self.rel_to_user_x(-0.5)
    end_y = self.rel_to_user_y(end_y)
    xdiff = x - left_x
    ydiff = y - end_y
    
    self.ctx.rel_line_to(-xdiff, -ydiff/2)
    self.ctx.rel_line_to(+xdiff, -ydiff/2)

  def flag_right(self, end_y):
    x, y = self.ctx.get_current_point()
    right_x = self.rel_to_user_x(0.5)
    end_y = self.rel_to_user_y(end_y)
    xdiff = right_x - x
    ydiff = y - end_y
    
    self.ctx.rel_line_to(+xdiff, -ydiff/2)
    self.ctx.rel_line_to(-xdiff, -ydiff/2)

  def cross(self, m, b, width):
    x, y = self.ctx.get_current_point()

    self.move_to(width * -0.5, b+m*width*-0.5)
    self.ctx.line_to(self.rel_to_user_x(width * 0.5), self.rel_to_user_y(b+m*width*0.5))
    
  def arc(self, rel_x, rel_y, rad, angle_1, angle_2):
    self.ctx.save()
    self.ctx.new_sub_path()
    self.ctx.translate(self.cursor_x, self.cursor_y)
    self.ctx.scale(self.x_scaled, self.y_scaled)
    self.ctx.set_line_width(self.LINE_WIDTH/self.x_scaled*0.75)
    self.ctx.arc(rel_x, rel_y, rad, angle_1, angle_2)
    self.stroke()
    self.ctx.restore()

  def move_to(self, rel_x, rel_y):
    self.ctx.move_to(self.rel_to_user_x(rel_x), self.rel_to_user_y(rel_y))

  def rel_move(self, dx, dy):
    self.ctx.rel_move_to(dx*self.x_scaled, dy*self.y_scaled)

  def line_to(self, rel_x, rel_y):
    self.ctx.line_to(self.rel_to_user_x(rel_x), self.rel_to_user_y(rel_y))

  def curve_to(self, x1, y1, x2, y2, x3, y3):
    self.ctx.curve_to(self.rel_to_user_x(x1), self.rel_to_user_y(y1), self.rel_to_user_x(x2), self.rel_to_user_y(y2), self.rel_to_user_x(x3), self.rel_to_user_y(y3))

  def bottom_triangle(self):
    self.move_to(0, 0.5)
    self.v_to_bottom()
    self.cross(0, 1, 1)

  def top_triangle(self):
    self.move_to(0, 0.5)
    self.v_to_top()
    self.cross(0, 0, 1)

  def not_implemented(self):
    pass

  def A(self):
    self.init_char()
    self.vert(1)
    self.stroke()  

  def B(self):      
    self.init_char()
    self.vert(0.65)
    self.v_to_bottom()
    self.stroke()

  def C(self):      
    self.init_char(0.15, 0)
    self.vert(1)
    self.flag_left(0.5)
    self.stroke()

  def D(self):
    self.init_char()
    self.vert(1)
    self.stroke()
    self.cross(0.5, 0.75, 0.9)
    self.stroke()

  def E(self):
    self.init_char()
    self.vert(0.75)
    self.stroke()
    self.arc(0, 0.5, 0.5, 0, -math.pi)
    self.stroke()

  def F(self):
    self.init_char()
    self.move_to(0, 0.35)
    self.v_to_top()
    self.vert(0.65)
    self.stroke()

  def G(self):
    self.init_char(0, 0.5)
    self.v_to_bottom()
    self.v_to_top()
    self.stroke()

  def H(self):
    self.init_char(0, 0.5)
    self.v_to_top()
    self.bottom_triangle()
    self.stroke()

  def I(self):
    self.init_char(0, 0.5)
    self.v_to_top()
    self.vert(0.5)
    self.stroke()
    self.cross(0, 0.75, 0.65)
    self.stroke()

  def J(self):
    self.init_char(-0.5, 1)
    self.curve_to(0, 0.7, 1, 0.35, 0, 0)
    self.curve_to(-1, 0.35, 0, 0.65, 0.5, 1)
    self.stroke()

  def K(self):
    self.init_char(-0.15, 0)
    self.vert(1)
    self.flag_right(0.5)
    self.stroke()
  
  def L(self):
    self.init_char(-0.15)
    self.vert(1)
    self.move_to(-0.15, 0.5)
    self.flag_right(0)
    self.stroke()
  
  def M(self):
    self.init_char()
    self.top_triangle()
    self.stroke()
    self.move_to(0, 0.5)
    self.v_to_bottom()
    self.stroke()

  def N(self):
    self.init_char()
    self.vert(1)
    self.flag_left(0.5)
    self.flag_right(0)
    self.stroke()
  
  def O(self):
    self.init_char(-0.15, 0)
    self.vert(1)
    self.rel_move(0, -0.5)
    self.flag_right(0)
    self.stroke()
    self.cross(0.25, 0.75, 0.75)
    self.stroke()

  def P(self):
    self.init_char()
    self.top_triangle()
    self.stroke()
    self.arc(0, 1, 0.5, math.pi, 0)
    self.stroke()

  def Q(self):
    self.init_char()
    self.vert(1)
    self.stroke()
    self.cross(-0.5, 0.25, 0.9)
    self.stroke()
  
  def R(self):
    self.init_char()
    self.vert(0.5)
    self.v_to_bottom()
    self.stroke()
    self.cross(0, 0.25, 0.65)
    self.stroke()

  def S(self):
    self.init_char(-0.15, 0)
    self.vert(1)
    self.flag_right(0.5)
    self.stroke()
    self.cross(-0.25, 0.25, 0.75)
    self.stroke()

  def T(self):
    self.init_char()
    self.vert(1)
    self.stroke()
    self.cross(-0.5, 0.25, 1)
    self.stroke()
    self.cross(0.5, 0.75, 1)
    self.stroke()
  
  def U(self):
    self.init_char()
    self.arc(0, 0.75, 0.5, math.pi, 0)
    self.stroke()
    self.move_to(0, 0.1)
    self.vert(0.4)
    self.stroke()
  
  def V(self):
    self.init_char(0, 0.25) 
    self.vert(0.75)
    self.stroke()
    self.arc(0, 0.5, 0.5, math.pi, 0)
    self.stroke()

  def W(self):
    self.init_char(-0.5, 0)
    self.curve_to(0, 0.3, 1, 0.65, 0, 1)
    self.curve_to(-1, 0.65, 0, 0.3, 0.5, 0)
    self.stroke()
  
  def X(self):
    self.init_char()
    self.bottom_triangle()
    self.stroke()
    self.arc(0, 0, 0.5, 0, -math.pi)
    self.stroke()

  def Y(self):
    self.init_char()
    self.arc(0, 0.25, 0.5, 0, math.pi)
    self.stroke()
    self.move_to(0, 0.5)
    self.vert(0.4)
    self.stroke()

  def Z(self):
    self.init_char()
    self.arc(0, 0.25, 0.25, 0, 2 * math.pi)
    self.stroke()
    self.arc(0, 0.75, 0.25, 0, 2 * math.pi)
    self.stroke()

def main():
  
  with open("input.txt", "r") as infile:
    lines = infile.readlines()
  line_lengths = [len(x) for x in lines]

  cw = CharacterWriter(1, max(line_lengths), len(lines))

  for line in lines:
    for char in line:
      rune_char = char.upper()
      if (rune_char == "\n"):
        cw.newline()
      else:
        cw.runes.setdefault(rune_char, lambda : cw.advance_cursor)()
        cw.advance_cursor()
  
  cw.export_image(lines[0].strip("\n") + ".png")

if __name__ == "__main__":
  main()
