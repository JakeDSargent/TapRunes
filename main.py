#!/usr/bin/env python

import math
import cairo

CHAR_WIDTH, CHAR_HEIGHT = 0.5, 0.75

def A(ctx, topx, topy, scale):
  ctx.new_path()
  ctx.move_to(topx, topy) 
  ctx.rel_line_to(0, 1 * CHAR_HEIGHT * scale)
  ctx.stroke()  

def B(ctx, topx, topy, scale):
  ctx.new_path()
  ctx.move_to(topx, topy)
  ctx.rel_line_to(0, scale * CHAR_HEIGHT * 0.5)
  ctx.rel_line_to(-0.5 * CHAR_WIDTH * scale, 0.5 * CHAR_HEIGHT * scale)
  ctx.rel_move_to(0.5 * CHAR_WIDTH * scale, -0.5 * CHAR_HEIGHT * scale)
  ctx.rel_line_to(0.5 * CHAR_WIDTH * scale, 0.5 * CHAR_HEIGHT * scale)
  ctx.stroke()

def C(ctx, topx, topy, scale):
  ctx.new_path()
  ctx.move_to(topx, topy)
  ctx.rel_line_to(0, 1 * CHAR_HEIGHT * scale)
  ctx.rel_line_to(-0.5 * CHAR_WIDTH * scale, -0.25 * CHAR_HEIGHT * scale)
  ctx.rel_line_to(0.5 * CHAR_WIDTH * scale, -0.25 * CHAR_HEIGHT * scale)
  ctx.stroke()

def D(ctx, topx, topy, scale):
  ctx.new_path()
  ctx.move_to(topx, topy)
  ctx.rel_line_to(0, 1 * CHAR_HEIGHT * scale)
  ctx.stroke()
  ctx.move_to(topx, topy)
  ctx.rel_move_to(-0.5 * CHAR_WIDTH * scale, 0.6 * CHAR_HEIGHT * scale)
  ctx.rel_line_to(1 * CHAR_WIDTH * scale, 0.33 * CHAR_HEIGHT * scale)
  ctx.stroke()

def E(ctx, topx, topy, scale):
  ctx.new_path()
  ctx.move_to(topx, topy)
  ctx.rel_line_to(0, 0.675 * CHAR_HEIGHT * scale)
  ctx.stroke()
  ctx.arc(topx, topy + 0.6 * CHAR_HEIGHT * scale, CHAR_WIDTH * scale / 2, 0, -math.pi)
  ctx.stroke() 

def main():

  WIDTH, HEIGHT = 256, 256

  surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
  ctx = cairo.Context(surface)

  ctx.scale(WIDTH, HEIGHT)  # Normalizing the canvas

  pat = cairo.LinearGradient(0.0, 0.0, 0.0, 1.0)
  pat.add_color_stop_rgba(1, 0.7, 0, 0, 0.5)  # First stop, 50% opacity
  pat.add_color_stop_rgba(0, 0.9, 0.7, 0.2, 1)  # Last stop, 100% opacity

  #ctx.rectangle(0, 0, 1, 1)  # Rectangle(x0, y0, x1, y1)
  ctx.set_source(pat)
  #ctx.fill()

  #ctx.set_source_rgb(0.3, 0.2, 0.5)  # Solid color
  ctx.set_line_width(0.01)

  curser_x, curser_y = CHAR_WIDTH / 2, 0.1
  scale = 0.6

  D(ctx, curser_x, curser_y, scale)
  curser_x += CHAR_WIDTH * scale
  B(ctx, curser_x, curser_y, scale)
  curser_x += CHAR_WIDTH * scale
  E(ctx, curser_x, curser_y, scale)

  surface.write_to_png("example.png")  # Output to PNG

if __name__ == "__main__":
  main()
