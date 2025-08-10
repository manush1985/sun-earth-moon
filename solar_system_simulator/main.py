import pygame
from pygame.locals import *
from OpenGL.GL import *
import math
import numpy as np
import os

def load_texture(filename):
    texture_surface = pygame.image.load(filename)
    texture_data = pygame.image.tostring(texture_surface, "RGB", 1)
    width = texture_surface.get_width()
    height = texture_surface.get_height()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)

    return texture_id

def draw_sphere(radius, lats, longs):
    for i in range(lats):
        lat0 = np.pi * (-0.5 + float(i) / lats)
        z0  = radius * np.sin(lat0)
        zr0 = radius * np.cos(lat0)

        lat1 = np.pi * (-0.5 + float(i + 1) / lats)
        z1 = radius * np.sin(lat1)
        zr1 = radius * np.cos(lat1)

        glBegin(GL_QUAD_STRIP)
        for j in range(longs + 1):
            lng = 2 * np.pi * float(j) / longs
            x = np.cos(lng)
            y = np.sin(lng)

            # Vertex 1 (bottom of strip)
            u = float(j) / longs
            v0 = float(i) / lats
            glNormal3f(x * zr0, y * zr0, z0)
            glTexCoord2f(u, v0)
            glVertex3f(x * zr0, y * zr0, z0)

            # Vertex 2 (top of strip)
            v1 = float(i + 1) / lats
            glNormal3f(x * zr1, y * zr1, z1)
            glTexCoord2f(u, v1)
            glVertex3f(x * zr1, y * zr1, z1)
        glEnd()

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Solar System Simulator - Press 'T' to toggle tilt")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    aspect_ratio = display[0] / display[1]
    fov_y = 45
    near_clip = 0.1
    far_clip = 100.0

    top = math.tan(math.radians(fov_y) / 2.0) * near_clip
    bottom = -top
    right = top * aspect_ratio
    left = -right

    glFrustum(left, right, bottom, top, near_clip, far_clip)

    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

    # Lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    # Texturing
    glEnable(GL_TEXTURE_2D)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    earth_texture = load_texture(os.path.join(script_dir, "textures", "earth.jpg"))
    moon_texture = load_texture(os.path.join(script_dir, "textures", "moon.jpg"))

    # Camera state
    camera_x_angle = 20
    camera_y_angle = 0
    camera_zoom = -30
    mouse_down = False
    last_mouse_x = 0
    last_mouse_y = 0

    # Earth tilt state
    earth_tilt = 23.5
    tilt_enabled = True

    # Animation parameters
    earth_rev_speed = 360 / 20
    earth_rot_speed = 360 / 2
    moon_rev_speed = 360 / 5

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEMOTION:
                if mouse_down:
                    dx = event.pos[0] - last_mouse_x
                    dy = event.pos[1] - last_mouse_y
                    camera_y_angle += dx * 0.5
                    camera_x_angle += dy * 0.5
                last_mouse_x, last_mouse_y = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True
                elif event.button == 4:
                    camera_zoom = min(-5, camera_zoom + 1)
                elif event.button == 5:
                    camera_zoom = max(-90, camera_zoom - 1)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    tilt_enabled = not tilt_enabled

        time_sec = pygame.time.get_ticks() / 1000.0

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        glTranslatef(0, 0, camera_zoom)
        glRotatef(camera_x_angle, 1, 0, 0)
        glRotatef(camera_y_angle, 0, 1, 0)

        glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 0, 1])

        # Sun
        glPushMatrix()
        glDisable(GL_TEXTURE_2D)
        glColor3f(1.0, 1.0, 0.0)
        draw_sphere(2, 32, 32)
        glEnable(GL_TEXTURE_2D)
        glPopMatrix()

        # Earth and Moon system
        glPushMatrix()
        earth_rev_angle = time_sec * earth_rev_speed
        glRotatef(earth_rev_angle, 0, 1, 0)
        glTranslatef(10, 0, 0)

        # Earth's axial tilt and rotation
        glPushMatrix()
        if tilt_enabled:
            glRotatef(earth_tilt, 0, 0, -1)
        earth_rot_angle = time_sec * earth_rot_speed
        glRotatef(earth_rot_angle, 0, 1, 0)
        glColor3f(1.0, 1.0, 1.0) # Set color to white for texture
        glBindTexture(GL_TEXTURE_2D, earth_texture)
        draw_sphere(0.5, 32, 32)
        glPopMatrix()

        # Moon's revolution
        glPushMatrix()
        moon_rev_angle = time_sec * moon_rev_speed
        glRotatef(moon_rev_angle, 0, 1, 0)
        glTranslatef(2, 0, 0)
        glColor3f(1.0, 1.0, 1.0) # Set color to white for texture
        glBindTexture(GL_TEXTURE_2D, moon_texture)
        draw_sphere(0.2, 32, 32)
        glPopMatrix()

        glPopMatrix()

        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()
