import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import pywavefront
from PIL import Image


def render_top_view(obj_file: str):
    scene_data = load_scene(obj_file)
    return get_display(scene_data)


def load_scene(obj_file: str) -> tuple:
    scene = pywavefront.Wavefront(obj_file, collect_faces=True)

    scene_box = (scene.vertices[0], scene.vertices[0])
    for vertex in scene.vertices:
        min_v = [min(scene_box[0][i], vertex[i]) for i in range(3)]
        max_v = [max(scene_box[1][i], vertex[i]) for i in range(3)]
        scene_box = (min_v, max_v)

    scene_size = [scene_box[1][i] - scene_box[0][i] for i in range(3)]
    max_scene_size = max(scene_size)
    scaled_size = 5
    scene_scale = [scaled_size / max_scene_size for i in range(3)]
    scene_trans = [-(scene_box[1][i] + scene_box[0][i]) / 2 for i in range(3)]

    return scene_scale, scene_trans, scene


def get_display(scene_data: tuple) -> Image:
    display = (600, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 1, 500.0)
    glTranslatef(0.0, 0.0, -6.5)
    glRotatef(90, 1, 0, 0)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    draw_model(*scene_data)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    pix = glReadPixels(0, 0, *display, GL_RGB, GL_UNSIGNED_BYTE)
    image = Image.frombytes(mode="RGB", size=display, data=pix)
    return image


def draw_model(scene_scale, scene_trans, scene):
    glPushMatrix()
    glScalef(*scene_scale)
    glTranslatef(*scene_trans)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    color_axe = 1

    for mesh in scene.mesh_list:
        max_height, min_height = float("-inf"), float("inf")
        for face in mesh.faces:
            for vertex_i in face:
                height = scene.vertices[vertex_i][color_axe]
                if height > max_height:
                    max_height = height
                elif height < min_height:
                    min_height = height

        min_height -= (max_height - min_height) // 4

        glBegin(GL_TRIANGLES)
        for face in mesh.faces:
            for vertex_i in face:
                height = scene.vertices[vertex_i][color_axe]
                color = 1
                if max_height != 0:
                    color = (height - min_height) / max_height

                glColor3f(color, color, color)
                glVertex3f(*scene.vertices[vertex_i])
        glEnd()

    glPopMatrix()

