#!/usr/bin/env python

from math import pi, sin, cos
import cairo


class SpellWriter:
  GLYPH_WIDTH, GLYPH_HEIGHT = 500, 500
  LINE_WIDTH = GLYPH_WIDTH // 10
  XPAD, YPAD = LINE_WIDTH * 2, LINE_WIDTH * 4

  def __init__(self,
               scale,
               char_width=1,
               char_height=1,
               ctx=None,
               surface=None):
    self.process_scale(scale)
    self.cursor_x = self.XPAD + self.LINE_WIDTH + self.x_scaled / 2
    self.cursor_y = self.YPAD + self.LINE_WIDTH + self.y_scaled / 2
    self.x_home = self.cursor_x
    self.y_home = self.cursor_y
    if ctx is not None and surface is not None:
      self.ctx = ctx
      self.surface = surface
      self.ctx.set_line_width(self.LINE_WIDTH)
      self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    else:
      self.generate_default_context()

  def generate_default_context(self):
    pixel_width = int((self.x_scaled + self.XPAD * 2) + 2 * self.LINE_WIDTH)
    pixel_height = int((self.y_scaled + self.YPAD) + 2 * self.LINE_WIDTH)
    self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixel_width,
                                      pixel_height)
    ctx = cairo.Context(self.surface)

    pat = cairo.LinearGradient(0.0, 0.0, 0.0, pixel_height)
    # add_color_stop_rbga(offset, % red, % green, % blue, % opacity)
    pat.add_color_stop_rgba(1, 1, 0, 0, 1)
    pat.add_color_stop_rgba(0.5, 0, 1, 0, 1)
    pat.add_color_stop_rgba(0, 0, 0, 1, 1)

    ctx.set_source(pat)
    self.ctx = ctx

    self.ctx.set_line_width(self.LINE_WIDTH)
    self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)

  def export_image(self, filename="example.png"):
    self.surface.write_to_png(filename)  # Output to PNG

  def process_scale(self, scale):
    self.scale = scale
    self.x_scaled = self.GLYPH_WIDTH * scale
    self.y_scaled = self.GLYPH_HEIGHT * scale
    self.XPAD *= scale
    self.YPAD *= scale
    self.LINE_WIDTH *= scale

  def rel_to_user_x(self, rel_x):
    return rel_x * self.x_scaled + self.cursor_x

  def rel_to_user_y(self, rel_y):
    return rel_y * self.y_scaled + self.cursor_y

  def x_y_from_radius(self, angle, radius):
    x = sin(angle) * radius
    y = cos(angle) * radius
    if (pi < angle < 2 * pi):
      y *= -1
    if (0.5 * pi < angle < 1.5 * pi):
      x *= -1

    return x, y

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

  def stroke(self):
    self.ctx.stroke()

  def init_cursor(self, rel_x=0, rel_y=0):
    self.ctx.new_path()
    self.move_to(rel_x, rel_y)

  def arc(self, rel_x, rel_y, rad, angle_1, angle_2):
    self.ctx.save()
    self.ctx.new_sub_path()
    self.ctx.translate(self.cursor_x, self.cursor_y)
    self.ctx.scale(self.x_scaled, self.y_scaled)
    self.ctx.set_line_width(self.LINE_WIDTH / self.x_scaled * 0.75)
    self.ctx.arc(rel_x, rel_y, rad, angle_1, angle_2)
    self.stroke()
    self.ctx.restore()

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


def main():

  cw = SpellWriter(1)
  cw.init_cursor()
  cw.arc(0, 0, 0.7, 0, 2 * pi)
  cw.export_image("spell_card" + ".png")


if __name__ == "__main__":
  main()
