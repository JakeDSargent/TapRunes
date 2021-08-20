#!/usr/bin/env python

import math
import cairo


class CharacterWriter:
  CHAR_WIDTH, CHAR_HEIGHT = 50, 80
  LINE_WIDTH = int(CHAR_WIDTH / 12)
  XPAD, YPAD = LINE_WIDTH * 2, LINE_WIDTH * 4

  STYLES = {"curved":   0,
            "diamond":  1,
            "square":   2,
            "hex1":     3,
            "hex2":     4,
            "chamfer":  5,
            "octogon":  6}

  def __init__(self,
         scale,
         char_width=1,
         char_height=1,
         ctx=None,
         surface=None):
    self.process_scale(scale)
    self.cursor_x = self.XPAD + self.x_scaled / 2
    self.cursor_y = self.YPAD
    self.x_home = self.cursor_x
    self.y_home = self.cursor_y
    if ctx is not None and surface is not None:
      self.ctx = ctx
      self.surface = surface
      self.ctx.set_line_width(self.LINE_WIDTH)
      self.ctx.set_line_join(cairo.LINE_JOIN_ROUND)
      self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    else:
      self.generate_default_context(char_width, char_height)
    self.style = self.STYLES["curved"]

    self.runes = {
      "A": self.A,
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
      "AA": self.AA,
      "BB": self.BB,
      "CC": self.CC,
      "CK": self.CK,
      "KC": self.KC,
      "DD": self.DD,
      "EE": self.EE,
      "FF": self.FF,
      "GG": self.GG,
      "HH": self.HH,
      "II": self.II,
      "JJ": self.JJ,
      "KK": self.KK,
      "LL": self.LL,
      "MM": self.MM,
      "NN": self.NN,
      "OO": self.OO,
      "PP": self.PP,
      "QQ": self.QQ,
      "RR": self.RR,
      "SS": self.SS,
      "TT": self.TT,
      "UU": self.UU,
      "VV": self.VV,
      "WW": self.WW,
      "XX": self.XX,
      "YY": self.YY,
      "ZZ": self.ZZ,
      "BF": self.BF,
      "CL": self.CL,
      "DQ": self.DQ,
      "EV": self.EV,
      "FB": self.FB,
      "HM": self.HM,
      "IR": self.IR,
      "JW": self.JW,
      "KL": self.KL,
      "LC": self.LC,
      "LK": self.LK,
      "MH": self.MH,
      "OS": self.OS,
      "PX": self.PX,
      "QD": self.QD,
      "RI": self.RI,
      "SO": self.SO,
      "UY": self.UY,
      "VE": self.VE,
      "WJ": self.WJ,
      "XP": self.XP,
      "YU": self.YU,
      "\n": self.newline,
      "" : self.draw_nothing,
      " ": self.draw_nothing,
      "*": self.action,
      "**": self.bonus_action
    }

    self.numeric_runes = {
      0: self.ZERO,
      1: self.ONE,
      2: self.TWO,
      3: self.THREE,
      4: self.FOUR,
      5: self.FIVE
    }

  def generate_default_context(self, char_width, char_height):
    pixel_width = int(char_width * (self.x_scaled + self.XPAD) +
              2 * self.LINE_WIDTH)
    pixel_height = int(char_height * (self.y_scaled + self.YPAD) +
               2 * self.LINE_WIDTH)
    self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixel_width,
                      pixel_height)
    ctx = cairo.Context(self.surface)

    pat = cairo.LinearGradient(0.0, 0.0, 0.0, pixel_height)
    # add_color_stop_rbga(offset, % red, % green, % blue, % opacity)
    pat.add_color_stop_rgba(1, 224/255, 160/255, 255/255, 1)
    pat.add_color_stop_rgba(0.5, 170/255, 207/255, 255/255, 1)
    pat.add_color_stop_rgba(0, 175/255, 31/255, 255/255, 1)

    ctx.set_source_rgb(5/255, 21/255, 9/255)
    ctx.rectangle(0,0,pixel_width, pixel_height)
    ctx.fill() 

    ctx.set_source(pat)
    self.ctx = ctx

    self.ctx.set_line_width(self.LINE_WIDTH)
    self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)

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

  def flag(self, end_y, tip_x):
    x, y = self.ctx.get_current_point()
    tip_x = self.rel_to_user_x(tip_x)
    end_y = self.rel_to_user_y(end_y)
    xdiff = x - tip_x
    ydiff = y - end_y

    self.ctx.rel_line_to(-xdiff, -ydiff / 2)
    self.ctx.rel_line_to(+xdiff, -ydiff / 2)

  def flag_left(self, end_y):
    self.flag(end_y, -0.5)

  def flag_right(self, end_y, tip_x=0.5):
    self.flag(end_y, 0.5)

  def cross(self, m, b, width):
    x, y = self.ctx.get_current_point()

    self.move_to(width * -0.5, b + m * width * -0.5)
    self.ctx.line_to(self.rel_to_user_x(width * 0.5),
             self.rel_to_user_y(b + m * width * 0.5))

  def arc(self, rel_x, rel_y, rad, angle_1, angle_2):
    if self.style == self.STYLES["curved"]:
      self.ctx.save()
      self.ctx.new_sub_path()
      self.ctx.translate(self.cursor_x, self.cursor_y)
      self.ctx.scale(self.x_scaled, self.y_scaled)
      self.ctx.set_line_width(self.LINE_WIDTH / self.x_scaled * 0.75)
      self.ctx.arc(rel_x, rel_y, rad, angle_1, angle_2)
      self.stroke()
      self.ctx.restore()
    else:
      if self.style == self.STYLES["diamond"]:
        if (angle_2 == angle_1 + 2 * math.pi):  # circle
          self.move_to(rel_x - rad, rel_y)
          self.line_to(rel_x, rel_y - rad)
          self.line_to(rel_x + rad, rel_y)

          self.line_to(rel_x, rel_y + rad)
          self.line_to(rel_x - rad, rel_y)
        elif (angle_1 == 0):  # half down
          self.move_to(rel_x + rad, rel_y)
          self.line_to(rel_x, rel_y + rad)
          self.line_to(rel_x - rad, rel_y)
        else:  # half up
          self.move_to(rel_x - rad, rel_y)
          self.line_to(rel_x, rel_y - rad)
          self.line_to(rel_x + rad, rel_y)
      elif self.style == self.STYLES["square"]:
        if (angle_2 == angle_1 + 2 * math.pi):  # circle
          self.move_to(rel_x - rad, rel_y)
          self.line_to(rel_x - rad, rel_y - rad)
          self.line_to(rel_x + rad, rel_y - rad)
          self.line_to(rel_x + rad, rel_y)

          self.line_to(rel_x + rad, rel_y + rad)
          self.line_to(rel_x - rad, rel_y + rad)
          self.line_to(rel_x - rad, rel_y)
        elif (angle_1 == 0):  # half down
          self.move_to(rel_x + rad, rel_y)

          self.line_to(rel_x + rad, rel_y + rad)
          self.line_to(rel_x - rad, rel_y + rad)
          self.line_to(rel_x - rad, rel_y)
        else:  # half up
          self.move_to(rel_x - rad, rel_y)
          self.line_to(rel_x - rad, rel_y - rad)
          self.line_to(rel_x + rad, rel_y - rad)
          self.line_to(rel_x + rad, rel_y)
      elif self.style == self.STYLES["hex1"]:
        if (angle_2 == angle_1 + 2 * math.pi):  # circle
          self.move_to(rel_x - rad, rel_y)
          self.line_to(rel_x - rad / 2, rel_y - rad)
          self.line_to(rel_x + rad / 2, rel_y - rad)
          self.line_to(rel_x + rad, rel_y)
          self.line_to(rel_x + rad / 2, rel_y + rad)
          self.line_to(rel_x - rad / 2, rel_y + rad)
          self.line_to(rel_x - rad, rel_y)
        elif (angle_1 == 0):  # half down
          self.move_to(rel_x + rad, rel_y)
          self.line_to(rel_x + rad / 2, rel_y + rad)
          self.line_to(rel_x - rad / 2, rel_y + rad)
          self.line_to(rel_x - rad, rel_y)
        else:  # half up
          self.move_to(rel_x - rad, rel_y)
          self.line_to(rel_x - rad / 2, rel_y - rad)
          self.line_to(rel_x + rad / 2, rel_y - rad)
          self.line_to(rel_x + rad, rel_y)
      elif self.style == self.STYLES["hex2"]:
        if (angle_2 == angle_1 + 2 * math.pi):  # circle
          self.move_to(rel_x - rad, rel_y)
          self.line_to(rel_x - rad, rel_y - rad/2)
          self.line_to(rel_x, rel_y - rad)
          self.line_to(rel_x + rad, rel_y - rad/2)
          self.line_to(rel_x + rad, rel_y)

          self.line_to(rel_x + rad, rel_y + rad/2)
          self.line_to(rel_x, rel_y + rad)
          self.line_to(rel_x - rad, rel_y + rad/2)
          self.line_to(rel_x - rad, rel_y)
        elif (angle_1 == 0):  # half down
          self.move_to(rel_x + rad, rel_y)
          self.line_to(rel_x + rad, rel_y + rad/2)
          self.line_to(rel_x, rel_y + rad)
          self.line_to(rel_x - rad, rel_y + rad/2)
          self.line_to(rel_x - rad, rel_y)
        else:  # half up
          self.move_to(rel_x - rad, rel_y)
          self.line_to(rel_x - rad, rel_y - rad/2)
          self.line_to(rel_x, rel_y - rad)
          self.line_to(rel_x + rad, rel_y - rad/2)
          self.line_to(rel_x + rad, rel_y)
      elif self.style == self.STYLES["chamfer"]:
        if (angle_2 == angle_1 + 2 * math.pi):  # circle
          self.move_to(rel_x - rad, rel_y)
          self.line_to(rel_x - rad, rel_y - 2*rad/3)
          self.line_to(rel_x - 2*rad/3, rel_y - rad)
          self.line_to(rel_x + 2*rad/3, rel_y - rad)
          self.line_to(rel_x + rad, rel_y - 2*rad/3)
          self.line_to(rel_x + rad, rel_y)

          self.line_to(rel_x + rad, rel_y + 2*rad/3)
          self.line_to(rel_x + 2*rad/3, rel_y + rad)
          self.line_to(rel_x - 2*rad/3, rel_y + rad)
          self.line_to(rel_x - rad, rel_y + 2*rad/3)
          self.line_to(rel_x - rad, rel_y)
        elif (angle_1 == 0):  # half down
          self.move_to(rel_x + rad, rel_y)

          self.line_to(rel_x + rad, rel_y + 2*rad/3)
          self.line_to(rel_x + 2*rad/3, rel_y + rad)
          self.line_to(rel_x - 2*rad/3, rel_y + rad)
          self.line_to(rel_x - rad, rel_y + 2*rad/3)
          self.line_to(rel_x - rad, rel_y)
        else:  # half up
          self.move_to(rel_x - rad, rel_y)
          self.line_to(rel_x - rad, rel_y - 2*rad/3)
          self.line_to(rel_x - 2*rad/3, rel_y - rad)
          self.line_to(rel_x + 2*rad/3, rel_y - rad)
          self.line_to(rel_x + rad, rel_y - 2*rad/3)
          self.line_to(rel_x + rad, rel_y)

      else:  # self.styles["octogon"]
        if (angle_2 == angle_1 + 2 * math.pi):  # circle
          self.move_to(rel_x - rad, rel_y)
          self.line_to(rel_x - rad, rel_y - rad/2)
          self.line_to(rel_x - rad/2, rel_y - rad)
          self.line_to(rel_x + rad/2, rel_y - rad)
          self.line_to(rel_x + rad, rel_y - rad/2)
          self.line_to(rel_x + rad, rel_y)

          self.line_to(rel_x + rad, rel_y + rad/2)
          self.line_to(rel_x + rad/2, rel_y + rad)
          self.line_to(rel_x - rad/2, rel_y + rad)
          self.line_to(rel_x - rad, rel_y + rad/2)
          self.line_to(rel_x - rad, rel_y)
        elif (angle_1 == 0):  # half down
          self.move_to(rel_x + rad, rel_y)

          self.line_to(rel_x + rad, rel_y + rad/2)
          self.line_to(rel_x + rad/2, rel_y + rad)
          self.line_to(rel_x - rad/2, rel_y + rad)
          self.line_to(rel_x - rad, rel_y + rad/2)
          self.line_to(rel_x - rad, rel_y)
        else:  # half up
          self.move_to(rel_x - rad, rel_y)
          self.line_to(rel_x - rad, rel_y - rad/2)
          self.line_to(rel_x - rad/2, rel_y - rad)
          self.line_to(rel_x + rad/2, rel_y - rad)
          self.line_to(rel_x + rad, rel_y - rad/2)
          self.line_to(rel_x + rad, rel_y)

  def move_to(self, rel_x, rel_y):
    self.ctx.move_to(self.rel_to_user_x(rel_x), self.rel_to_user_y(rel_y))

  def rel_move(self, dx, dy):
    self.ctx.rel_move_to(dx * self.x_scaled, dy * self.y_scaled)

  def line_to(self, rel_x, rel_y):
    self.ctx.line_to(self.rel_to_user_x(rel_x), self.rel_to_user_y(rel_y))

  def line(self, x1, y1, x2, y2):
    self.move_to(x1, y1)
    self.line_to(x2, y2)

  def curve_to(self, init_x, init_y, x1, y1, x2, y2, x3, y3):
    self.move_to(init_x, init_y)
    if self.style == self.STYLES["curved"]:
      self.ctx.curve_to(self.rel_to_user_x(x1), self.rel_to_user_y(y1),
                        self.rel_to_user_x(x2), self.rel_to_user_y(y2),
                        self.rel_to_user_x(x3), self.rel_to_user_y(y3))
    else:
      if (init_x <= x1 <= x2 <= x3 or x3 <= x2 <= x1 <= init_x):
        if init_y < 0.5:
          self.line_to(x1, y1/2)
          self.line_to(x2, y2/2)
          self.line_to(x3, y3)
        else:
          self.line_to(x1, y1/2 + 0.5)
          self.line_to(x2, y2/2 + 0.5)
          self.line_to(x3, y3)
      elif (init_y <= y1 <= y2 <= y3 or y3 <= y2 <= y1 <= init_y):
        self.line_to(x1 / 2, y1)
        self.line_to(x2 / 2, y2)
        self.line_to(x3, y3)
      else:
        self.line_to(x1, y1)
        self.line_to(x2, y2)
        self.line_to(x3, y3)

  def bottom_triangle(self):
    self.move_to(0, 0.5)
    self.v_to_bottom()
    self.cross(0, 1, 1)

  def top_triangle(self):
    self.move_to(0, 0.5)
    self.v_to_top()
    self.cross(0, 0, 1)

  def draw_nothing(self):
    pass

  def action(self):
    self.init_char()
    self.line_to(-0.25, 0.5)
    self.line_to(0.25, 0.5)
    self.line_to(0, 1)
    self.stroke()

  def bonus_action(self):
    self.init_char()
    self.line_to(-0.2, 0.33)
    self.line_to(0.2, 0.33)
    self.line_to(-0.2, 0.67)
    self.line_to(0.2, 0.67)
    self.line_to(0, 1)
    self.stroke()

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
    self.arc(0, 0.5, 0.5, 0, math.pi)
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
    self.init_char()
    self.curve_to(-0.5, 0, 0, 0.3, 1, 0.65, 0, 1)
    self.curve_to(0, 1, -1, 0.65, 0, 0.3, 0.5, 0)
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
    self.arc(0, 0.8, 0.5, math.pi, 0)
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
    self.init_char()
    self.curve_to(-0.5, 1, 0, 0.7, 1, 0.35, 0, 0)
    self.curve_to(0, 0, -1, 0.35, 0, 0.65, 0.5, 1)
    self.stroke()

  def X(self):
    self.init_char()
    self.bottom_triangle()
    self.stroke()
    self.arc(0, 0.2, 0.5, 0, -math.pi)
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

  def AA(self):
    self.init_char(-0.2, 0)
    self.vert(1)
    self.stroke()
    self.move_to(0.2, 0)
    self.vert(1)
    self.stroke()

  def BB(self):
    self.init_char(-0.15, 0)
    self.vert(0.65)
    self.line_to(-0.5, 1)
    self.stroke()
    self.move_to(0.15, 0)
    self.vert(0.65)
    self.line_to(0.5, 1)
    self.stroke()

  def CC(self):
    self.init_char(0.4)
    self.vert(1)
    self.flag(0.5, -0.1)
    self.stroke()
    self.move_to(0, 0.5)
    self.flag(1, -0.5)
    self.stroke()

  def CK(self):
    self.init_char()
    self.vert(1)
    self.flag(0.5, -0.5)
    self.flag(1, 0.5)
    self.stroke()

  def KC(self):
    self.init_char()
    self.vert(1)
    self.move_to(-0.5, 0.5)
    self.flag(1, 0)
    self.stroke()
    self.move_to(0.5, 0.5)
    self.flag(1, 0)
    self.stroke()

  def DD(self):
    self.init_char()
    self.vert(1)
    self.stroke()
    self.cross(0.5, 0.85, 0.9)
    self.stroke()
    self.cross(0.5, 0.6, 0.9)
    self.stroke()

  def EE(self):
    self.init_char()
    self.vert(0.75)
    self.stroke()
    self.arc(0, 0.675, 0.325, 0, 2 * math.pi)
    self.stroke()

  def FF(self):
    self.init_char(-0.5, 0)
    self.line_to(-0.15, 0.35)
    self.vert(0.65)
    self.stroke()
    self.move_to(0.5, 0)
    self.line_to(0.15, 0.35)
    self.vert(0.65)
    self.stroke()

  def GG(self):
    self.init_char(0, 0.5)
    self.v_to_bottom()
    self.v_to_top()
    self.stroke()
    self.move_to(0, 0)
    self.vert(1)
    self.stroke()

  def HH(self):
    self.init_char(0, 0.5)
    self.v_to_top()
    self.bottom_triangle()
    self.stroke()
    self.move_to(0, 0)
    self.vert(1)
    self.stroke()

  def II(self):
    self.init_char(0, 0.5)
    self.v_to_top()
    self.vert(0.5)
    self.stroke()
    self.cross(0, 0.65, 0.65)
    self.stroke()
    self.cross(0, 0.85, 0.65)
    self.stroke()

  def JJ(self):
    self.init_char()
    self.curve_to(-0.5, 0, 0, 0.3, 1, 0.65, 0, 1)
    self.curve_to(0, 1, -1, 0.65, 0, 0.3, 0.5, 0)
    self.stroke()
    self.arc(0, 0.65, 0.175, 0, 2 * math.pi)
    self.stroke()

  def KK(self):
    self.init_char(-0.4)
    self.vert(1)
    self.flag(0.5, 0.1)
    self.stroke()
    self.move_to(0, 0.5)
    self.flag(1, 0.5)
    self.stroke()

  def LL(self):
    self.init_char(-0.4)
    self.vert(1)
    self.move_to(-0.4, 0.5)
    self.flag(0, 0.1)
    self.stroke()
    self.move_to(0, 0.5)
    self.flag(0, 0.5)
    self.stroke()

  def MM(self):
    self.init_char()
    self.top_triangle()
    self.stroke()
    self.move_to(0, 0.5)
    self.v_to_bottom()
    self.stroke()
    self.move_to(0, 0)
    self.vert(1)
    self.stroke()

  def NN(self):
    self.init_char()
    self.vert(1)
    self.flag_left(0.5)
    self.flag_right(0)
    self.move_to(0, 1)
    self.flag_right(0.5)
    self.flag_left(0)
    self.stroke()

  def OO(self):
    self.init_char(-0.15, 0)
    self.vert(1)
    self.rel_move(0, -0.5)
    self.flag_right(0)
    self.stroke()
    self.cross(0.25, 0.7, 0.75)
    self.stroke()
    self.cross(0.25, 0.9, 0.75)
    self.stroke()

  def PP(self):
    self.init_char()
    self.top_triangle()
    self.stroke()
    self.arc(0, 0.6, 0.35, -2 * math.pi, 0)
    self.stroke()

  def QQ(self):
    self.init_char()
    self.vert(1)
    self.stroke()
    self.cross(-0.5, 0.15, 0.9)
    self.stroke()
    self.cross(-0.5, 0.4, 0.9)
    self.stroke()

  def RR(self):
    self.init_char()
    self.vert(0.5)
    self.v_to_bottom()
    self.stroke()
    self.cross(0, 0.15, 0.65)
    self.stroke()
    self.cross(0, 0.35, 0.65)
    self.stroke()

  def SS(self):
    self.init_char(-0.15, 0)
    self.vert(1)
    self.flag_right(0.5)
    self.stroke()
    self.cross(-0.25, 0.15, 0.75)
    self.stroke()
    self.cross(-0.25, 0.35, 0.75)
    self.stroke()

  def TT(self):
    self.init_char(-0.10, 0)
    self.vert(1)
    self.stroke()
    self.move_to(0.2, 0)
    self.vert(1)
    self.stroke()
    self.cross(-0.5, 0.25, 1)
    self.stroke()
    self.cross(0.5, 0.75, 1)
    self.stroke()

  def UU(self):
    self.init_char()
    self.arc(0, 0.75, 0.5, math.pi, 0)
    self.stroke()
    self.move_to(-0.15, 0.1)
    self.vert(0.4)
    self.stroke()
    self.move_to(0.15, 0.1)
    self.vert(0.4)
    self.stroke()

  def VV(self):
    self.init_char(0, 0.25)
    self.vert(0.75)
    self.stroke()
    self.arc(0, 0.325, 0.325, 0, 2 * math.pi)
    self.stroke()

  def WW(self):
    self.init_char()
    self.curve_to(-0.5, 1, 0, 0.7, 1, 0.35, 0, 0)
    self.curve_to(0, 0, -1, 0.35, 0, 0.65, 0.5, 1)
    self.stroke()
    self.arc(0, 0.35, 0.175, 0, 2 * math.pi)
    self.stroke()

  def XX(self):
    self.init_char(0, 0.5)
    self.bottom_triangle()
    self.stroke()
    self.arc(0, 0.4, 0.35, -2 * math.pi, 0)
    self.stroke()

  def YY(self):
    self.init_char()
    self.arc(0, 0.25, 0.5, 0, math.pi)
    self.stroke()
    self.move_to(-0.15, 0.5)
    self.vert(0.4)
    self.stroke()
    self.move_to(0.15, 0.5)
    self.vert(0.4)
    self.stroke()

  def ZZ(self):
    self.init_char()
    self.arc(0, 0.25, 0.25, 0, 2 * math.pi)
    self.stroke()
    self.arc(0, 0.75, 0.25, 0, 2 * math.pi)
    self.stroke()
    self.arc(-0.25, 0.5, 0.25, 0, 2 * math.pi)
    self.stroke()
    self.arc(0.25, 0.5, 0.25, 0, 2 * math.pi)
    self.stroke()

  def BF(self):
    self.init_char()
    self.vert(0.25)
    self.flag_left(0.75)
    self.flag_right(0.25)
    self.stroke()
    self.move_to(0, 0.75)
    self.vert(0.25)
    self.stroke()

  def CL(self):
    self.init_char(0.2)
    self.vert(1)
    self.stroke()
    self.move_to(0.2, 0.75)
    self.flag(0.25, -0.4)
    self.stroke()

  def DQ(self):
    self.init_char()
    self.vert(1)
    self.stroke()
    self.cross(0, 0.5, 0.75)
    self.stroke()

  def EV(self):
    self.init_char()
    self.vert(1)
    self.stroke()
    self.arc(0, 0.2, 0.3, 0, math.pi)
    self.stroke()
    self.arc(0, 0.8, 0.3, -math.pi, 0)
    self.stroke()

  def FB(self):
    self.init_char(0, 0.4)
    self.v_to_top()
    self.vert(.2)
    self.v_to_bottom()
    self.stroke()

  def HM(self):
    self.init_char(0, 0.25)
    self.v_to_top()
    self.flag_right(0.75)
    self.flag_left(0.25)
    self.stroke()
    self.move_to(0, 0.75)
    self.v_to_bottom()
    self.stroke()
    self.cross(0, 0.5, 1)
    self.stroke()

  def IR(self):
    self.init_char(0, 0.4)
    self.v_to_top()
    self.vert(.2)
    self.v_to_bottom()
    self.stroke()
    self.cross(0, 0.5, 0.6)
    self.stroke()

  def JW(self):
    self.init_char(-0.5, 0)
    self.curve_to(-0.5, 0, 0, 0.3 * 0.75, 1, 0.65 * 0.75, 0, 1 * 0.75)
    self.curve_to(0, 1 * 0.75, -1, 0.65 * 0.75, 0, 0.3 * 0.75, 0.5,
            0 * 0.75)
    self.stroke()

    self.curve_to(-0.5, 1 * 0.75 + 0.25, 0, 0.7 * 0.75 + 0.25, 1,
            0.35 * 0.75 + 0.25, 0, 0 * 0.75 + 0.25)
    self.curve_to(0, 0 * 0.75 + 0.25, - 1, 0.35 * 0.75 + 0.25, 0,
            0.65 * 0.75 + 0.25, 0.5, 1)
    self.stroke()

  def KL(self):
    self.init_char(-0.2)
    self.vert(1)
    self.stroke()
    self.move_to(-0.2, 0.75)
    self.flag(0.25, 0.4)
    self.stroke()

  def LC(self):
    self.init_char(0.2)
    self.vert(1)
    self.flag(0.65, -0.3)
    self.move_to(0.2, 0.35)
    self.flag(0, -0.3)
    self.stroke()

  def LK(self):
    self.init_char(-0.2)
    self.vert(1)
    self.flag(0.65, 0.3)
    self.move_to(-0.2, 0.35)
    self.flag(0, 0.3)
    self.stroke()

  def MH(self):
    self.init_char(0, 0.25)
    self.v_to_top()
    self.flag_right(0.75)
    self.flag_left(0.25)
    self.stroke()
    self.move_to(0, 0.75)
    self.v_to_bottom()
    self.stroke()
    self.cross(0, 0, 1)
    self.stroke()
    self.cross(0, 1, 1)
    self.stroke()

  def OS(self):
    self.init_char(-0.1)
    self.vert(1)
    self.flag(0.65, 0.3)
    self.move_to(-0.1, 0.35)
    self.flag(0, 0.3)
    self.stroke()
    self.cross(0, 0.5, 0.75)
    self.stroke()

  def PX(self):
    self.init_char(0, 0.5)
    self.top_triangle()
    self.bottom_triangle()
    self.stroke()
    self.arc(0, 0.5, 0.35, 0, 2 * math.pi)
    self.stroke()

  def QD(self):
    self.init_char()
    self.vert(1)
    self.stroke()
    self.cross(0, 0.25, 0.6)
    self.stroke()
    self.cross(0, 0.75, 0.6)
    self.stroke()

  def RI(self):
    self.init_char()
    self.vert(0.25)
    self.flag_left(0.75)
    self.flag_right(0.25)
    self.stroke()
    self.move_to(0, 0.75)
    self.vert(0.25)
    self.stroke()
    self.cross(0, 0.125, 0.6)
    self.stroke()
    self.cross(0, 0.875, 0.6)
    self.stroke()

  def SO(self):
    self.init_char(-0.05)
    self.vert(1)
    self.stroke()
    self.move_to(-0.05, 0.75)
    self.flag(0.25, 0.4)
    self.stroke()
    self.cross(-0.25, 0.125, 0.6)
    self.stroke()
    self.cross(0.25, 0.875, 0.6)
    self.stroke()

  def UY(self):
    self.init_char()
    self.vert(0.3)
    self.stroke()
    self.move_to(0, 0.7)
    self.vert(0.3)
    self.arc(0, 0.5, 0.325, 0, 2 * math.pi)
    self.stroke()

  def VE(self):
    self.init_char(0, 0.25)
    self.vert(0.5)
    self.stroke()
    self.arc(0, 0.25, 0.25, math.pi, 2 * math.pi)
    self.arc(0, 0.75, 0.25, 0, math.pi)
    self.stroke()

  def WJ(self):
    self.init_char(-0.5, 1 / 2)
    self.curve_to(-0.5, 1 / 2, 0, 0.7 / 2, 1, 0.35 / 2, 0, 0 / 2)
    self.curve_to(0, 0 / 2, -1, 0.35 / 2, 0, 0.65 / 2, 0.5, 1 / 2)
    self.stroke()

    self.init_char()
    self.curve_to(-0.5, 0 / 2 + 0.5, 0, 0.3 / 2 + 0.5, 1, 0.65 / 2 + 0.5, 0, 1 / 2 + 0.5)
    self.curve_to(0, 1 / 2 + 0.5, -1, 0.65 / 2 + 0.5, 0, 0.3 / 2 + 0.5, 0.5, 0 / 2 + 0.5)
    self.stroke()

  def XP(self):
    self.init_char(0, 0.25)
    self.flag_left(0.75)
    self.flag_right(0.25)
    self.cross(0, 0.5, 1)
    self.stroke()
    self.arc(0, 0, 0.4, 0, math.pi)
    self.stroke()
    self.arc(0, 1, 0.4, math.pi, 2* math.pi)
    self.stroke()

  def YU(self):
    self.init_char(0, 0.2)
    self.vert(0.6)
    self.arc(0, 0, 0.4, 0, math.pi)
    self.stroke()
    self.arc(0, 1, 0.4, math.pi, 2* math.pi)
    self.stroke()

  def ZERO(self):
    # self.init_char(-0.5, 0)
    # self.flag(0.3, -0.2)
    # self.move_to(0.5, 0)
    # self.flag(0.3, 0.2)
    # self.cross(0, 0.15, 0.4)
    # self.stroke()

    self.init_char(-0.5, 0.05)
    self.vert(0.2)
    self.move_to(0.5, 0.05)
    self.vert(0.2)
    # self.line(-0.5, 0.15, -0.3, 0.15)
    # self.line(0.5, 0.15, 0.3, 0.15)
    self.stroke()

  def ONE(self):
    # self.init_char()
    # self.cross(0, 0.15, 0.8)
    # self.stroke()
    self.init_char(-0.5, 0.05)
    self.vert(0.2)
    self.move_to(0.5, 0.05)
    self.vert(0.2)
    self.cross(0, 0.15, 1)
    self.stroke()

  def TWO(self):
    self.init_char()
    self.line_to(-0.5, 0.3)
    self.move_to(0, 0)
    self.line_to(0.5, 0.3)
    self.stroke()

  def THREE(self):
    self.init_char()
    self.line_to(-0.5, 0.3)
    self.move_to(0, 0)
    self.line_to(0.5, 0.3)
    self.cross(0, 0.3, 1)
    self.stroke()

  def FOUR(self):
    self.init_char()
    self.vert(0.3)
    self.cross(0, 0.15, 0.4)
    self.stroke()

  def FIVE(self):
    self.init_char()
    self.arc(0, 0.15, 0.15, 0, 2 * math.pi)
    self.stroke()

    # self.init_char()
    # self.flag(0.3, -0.25)
    # self.flag(0, .25)
    # self.stroke()

  def write_rune(self, rune):
    self.runes[rune]()
    if rune != "\n":
      self.advance_cursor()

  def write_numeric_rune(self, rune):
    rune_val = int(rune)
    high = rune_val // 36
    rune_val -= high * 36
    mid = rune_val // 6
    rune_val -= mid * 6
    low = rune_val

    y_pos = self.cursor_y

    self.numeric_runes[high]()
    self.cursor_y = self.rel_to_user_y(0.35)
    self.numeric_runes[mid]()
    self.cursor_y = self.rel_to_user_y(0.35)
    self.numeric_runes[low]()

    self.cursor_y = y_pos
    self.advance_cursor()

  def write_inscription(self, inscription):
    for rune in inscription:
      if rune in self.runes.keys():
        self.write_rune(rune)
      elif rune.isnumeric():
        self.write_numeric_rune(rune)

  def parse_inscription(self, string):
    inscription = []
    for char in string:
      char = char.upper()
      if char.isnumeric():
        if len(inscription) >= 1 and inscription[-1][0] == "0":
          inscription[-1] = inscription[-1][-1] + char
          continue
        inscription.append("0" + char)
      else:
        if len(inscription) >= 1:
          if inscription[-1] + char in self.runes.keys():
            inscription[-1] += char
            continue
        inscription.append(char)
    return inscription

  def parse_file(self, filename):
    with open(filename, "r") as infile:
      lines = infile.readlines()
    inscription_lines = []
    for line in lines:
      inscription_lines.append(self.parse_inscription(line))
    insc_width = len(max(inscription_lines, key=len))
    insc_height = len(inscription_lines)
    return insc_width, insc_height, inscription_lines


def main():

  cw = CharacterWriter(1)
  cw.style = cw.STYLES["hex2"]
  width, height, insc_lines = cw.parse_file("input.txt")
  cw.generate_default_context(width, height)
  for inscription in insc_lines:
    cw.write_inscription(inscription)

  cw.export_image("output" + ".png")


def debug_print():
  cw = CharacterWriter(1)

  width, height, insc_lines = cw.parse_file("input.txt")
  cw.generate_default_context(width, height * len(cw.STYLES))
  for inscription in insc_lines:
    for style in [cw.STYLES[x] for x in cw.STYLES]:
      cw.style = style
      cw.write_inscription(inscription)

  cw.export_image("output" + ".png")


if __name__ == "__main__":
  main()
