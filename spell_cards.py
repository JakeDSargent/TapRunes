#!/usr/bin/env python

from math import pi, sin, cos
import cairo
import character_writer as CW
import random

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
      self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    else:
      self.generate_default_context()

    self.big_r = .1
    self.small_r = .08

    self.coords = {
      "LEVEL":    (0,0),
      "C/R":      (0,0),
      "CAST":     (0,0),
      "DURATION": (0,0),
      "TARGET":   (0,0),
      "SCHOOL":   (0,0),
      "DAMAGE":   (0,0),
      "RANGE":    (0,0)
    }
    self.ctx.save()
    self.writer_scale = scale / 1.5
    self.writer = CW.CharacterWriter(scale / 1.5, ctx=self.ctx, surface=self.surface)
    self.ctx.restore()

  def generate_default_context(self):
    pixel_width = int((self.x_scaled + self.XPAD * 2) + 2 * self.LINE_WIDTH)
    pixel_height = int((self.y_scaled + self.YPAD * 2) + 2 * self.LINE_WIDTH)
    self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixel_width,
                                      pixel_height)
    ctx = cairo.Context(self.surface)
    ctx.set_source_rgb(0, 0, 0)
    ctx.rectangle(0, 0, pixel_width, pixel_height)
    ctx.fill()
    pat = cairo.RadialGradient(self.cursor_x, self.cursor_y, 0.0, self.cursor_x, self.cursor_y, max(pixel_width, pixel_height)/2)
    # add_color_stop_rbga(offset, % red, % green, % blue, % opacity)
    num_stops = len(self.palette)*2
    for i in range(num_stops):
      r, g, b = self.palette[i%len(self.palette)]
      pat.add_color_stop_rgb(1/num_stops * i, r, g, b)

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

  def find_key_coords(self, rad3, rad5):
    inc3 = 2*pi/3
    base3 = pi*3/2
    
    inc5 = 2*pi/5
    base5 = pi/2 - 2*inc5
    self.coords["LEVEL"]    = self.x_y_from_angle(base3 + inc3 * 0, rad3)
    self.coords["C/R"]      = self.x_y_from_angle(base3 + inc3 * 1, rad3)
    self.coords["CAST"]     = self.x_y_from_angle(base3 + inc3 * 2, rad3)
    self.coords["DURATION"] = self.x_y_from_angle(base5 + inc5 * 0, rad5)
    self.coords["TARGET"]   = self.x_y_from_angle(base5 + inc5 * 1, rad5)
    self.coords["SCHOOL"]   = self.x_y_from_angle(base5 + inc5 * 2, rad5)
    self.coords["DAMAGE"]   = self.x_y_from_angle(base5 + inc5 * 3, rad5)
    self.coords["RANGE"]    = self.x_y_from_angle(base5 + inc5 * 4, rad5)

  def draw_sigil_circles(self):
    count = 0
    for key in self.coords:
      x, y = self.coords[key]
      if count < 3:
        self.overwriting_arc(x, y, self.big_r, 0, 2*pi)
      else:
        self.overwriting_arc(x, y, self.small_r, 0, 2*pi)
      count += 1

  def no_save(self):
    self.init_cursor()
    rad3, rad5 = .125, .4
    self.find_key_coords(rad3, rad5)
    keys = list(self.coords.keys())

    self.arc(0, 0, rad5, 0, 2 * pi)
    for i in range(5):
      x1, y1 = self.coords[keys[(i%5)+3]]
      x2, y2 = self.coords[keys[((i+1)%5)+3]]
      self.line(x1, y1, x2, y2)
      self.stroke()

    self.arc(0, 0, rad3+self.big_r, 0, 2*pi)
    self.draw_sigil_circles()
    self.draw_sigil("LEVEL", ["2"])
    self.draw_sigil("RANGE", ["60", "F"])
    self.draw_sigil("DAMAGE", ["0", "D", "4"])
    self.draw_CR_sigil(R="True")
    
  def draw_CR_sigil(self, C=False, R=False):
    self.ctx.save()
    x, y = self.coords["C/R"]
    self.ctx.new_sub_path()
    self.ctx.translate(self.cursor_x, self.cursor_y)
    self.ctx.scale(self.x_scaled, self.y_scaled)
    self.ctx.set_line_width(self.LINE_WIDTH / self.x_scaled * 0.75)
    self.ctx.arc(x, y, self.big_r, -pi/2, pi/2)
    self.ctx.restore()
    self.ctx.save()
    r,g,b = random.choice(self.palette)
    self.ctx.set_source_rgb(r, g, b)
    offset = self.big_r/2
    self.curve_to(x + 2*offset, y + offset, x - 2*offset, y - offset, x, y - self.big_r)
    if R:
      self.fill()
    else:
      self.stroke()
    self.ctx.restore()
  def draw_sigil(self, key, sigils):
    self.ctx.save() 
    self.ctx.set_source_rgb(1, 0.7, 1)
    x,y = self.coords[key]
    scale_shift = 1 - (0.15 * (len(sigils) - 1))
    if key in ["LEVEL", "C/R", "CAST"]:
      scale_shift *= self.big_r / self.small_r
    self.writer.process_scale(scale_shift)
    self.ctx.set_line_width(self.writer.LINE_WIDTH)
    if len(sigils) > 1:
      x_offset = (self.writer.x_scaled + self.writer.XPAD) / 2 * (len(sigils)-1)
    else:
      x_offset = 0
    y_offset = self.writer.y_scaled / 2
    self.writer.place_cursor(self.rel_to_user_x(x) - x_offset, self.rel_to_user_y(y) - y_offset)
    for sigil in sigils:
      if sigil.isnumeric():
        self.writer.write_numeric_rune(sigil)
      else:
        self.writer.write_rune(sigil)
    self.writer.process_scale(1 / scale_shift)
    self.ctx.restore()

def main():

  cw = SigilWriter(2)
  cw.no_save()
  
  
  cw.export_image("spell_card" + ".png")


if __name__ == "__main__":
  main()
