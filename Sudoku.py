# sudoku puzzel code from
# https://stackoverflow.com/questions/45471152/how-to-create-a-sudoku-puzzle-in-python
# author Alain T.
# license under CC BY-SA 4.0

# slightly modified to encapsulate as functions

from copy import deepcopy

base  = 3
side  = base*base

# pattern for a baseline valid solution
def pattern(r,c): return (base*(r%base)+r//base+c)%side

# randomize rows, columns and numbers (of valid base pattern)
from random import sample
def shuffle(s): return sample(s,len(s))

def solution_board():
    rBase = range(base) 
    rows  = [ g*base + r for g in shuffle(rBase) for r in shuffle(rBase) ] 
    cols  = [ g*base + c for g in shuffle(rBase) for c in shuffle(rBase) ]
    nums  = shuffle(range(1,base*base+1))

    # produce board using randomized baseline pattern
    board = [ [nums[pattern(r,c)] for c in cols] for r in rows ]

    return board

def puzzel_board(solution, ratio):
    board = deepcopy(solution)
    squares = side*side
    empties = int(squares * ratio)
    for p in sample(range(squares),empties):
        board[p//side][p%side] = 0
    
    return board

bl_info = {
    "name": "Sudoku",
    "author": "Latidoremi",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "N Panel > Sudoku",
    "description": "Sudoku Game",
    "category": "Games",
}


# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import numpy as np
from math import floor


levels=[
    ('Easy','Easy','',0),
    ('Normal','Normal','',1),
    ('Hard','Hard','',2),
    ('Insane','Insane','',3),
]

level_dict={
        'Easy':0.3, 
        'Normal':0.45, 
        'Hard':0.55, 
        'Insane':0.7}

states=[
    ('Start','Start','',0),
    ('Play','Play','',1),
    ('End','End','',2),
]

def draw_start(self, context):
    layout = self.layout
    scene = context.scene
    if scene.Sudoku_board:
        layout.operator('sudoku.set_state', text='Resume').state = 'Play'
    
    col = layout.column(align=True)
    col.operator('sudoku.play', text = 'Easy').level = 'Easy'
    col.operator('sudoku.play', text = 'Normal').level = 'Normal'
    col.operator('sudoku.play', text = 'Hard').level = 'Hard'
    col.operator('sudoku.play', text = 'Insane').level = 'Insane'
    

def draw_play(self, context):
    layout = self.layout
    scene = context.scene
    board = scene.Sudoku_board
    active_index = scene.Sudoku_active
    
    #draw board
    col = layout.column(align=True)
    for i, item in enumerate(board):
        if i%9 == 0:
            sub_row = col.row(align=True)
        
        if (i+9)%27 == 0: col.separator(factor=0.6)
        
        if i%3==0:
            row = sub_row.row(align=True)
        if i%9 in (3,6):
            row.separator()
        
        if item.puzzel_number!=0:
            if item.input_number==board[active_index].input_number:
                op_text = '['+str(item.puzzel_number)+']'
            else:
                op_text = '.'+str(item.puzzel_number)+'.'
        else:
            if item.input_number==board[active_index].input_number:
                op_text = ('['+str(item.input_number)+']' if item.input_number!=0 else '')
            else:
                op_text = (str(item.input_number) if item.input_number!=0 else '')
          
        row.operator('sudoku.set_active', text=op_text, depress=(active_index==i)).index = i

    #input
    row = layout.row(align = True)
    for i in range(10):
        op = row.operator('sudoku.set_number',text = (str(i) if i!=0 else ''))
        op.number = i
    
    layout.operator('sudoku.submit', icon='CHECKMARK')
    row = layout.column(align = True)
    row.operator('sudoku.reset', icon='FILE_REFRESH')
    row.operator('sudoku.randomize', icon= 'RNDCURVE')
    row.operator('sudoku.set_state', text='Quit', icon= 'LOOP_BACK').state='Start'
    
def draw_end(self, context):
    layout = self.layout
    scene = context.scene
    board = scene.Sudoku_board
    active_index = scene.Sudoku_active
    
    #draw board
    col = layout.column(align=True)
    for i, item in enumerate(board):
        if i%9 == 0:
            sub_row = col.row(align=True)
        
        if (i+9)%27 == 0: col.separator(factor=0.6)
        
        if i%3==0:
            row = sub_row.row(align=True)
        if i%9 in (3,6):
            row.separator()
        row.enabled=False
        row.operator('sudoku.set_active', text=str(item.input_number)).index = i
    
    row = layout.row()
    row.alert=True
    row.operator('sudoku.set_state', text='!!! You Win !!!',emboss=False).state='Start'

def check(context):
    scene = context.scene
    inputs = [item.input_number for item in scene.Sudoku_board]
    inputs_a = np.array(inputs)

    rows = inputs_a.reshape((9,9))
    columns =rows.T
    subgrids =[]
    for i in range(9):
        ix = floor(i/3)*3
        iy = (i%3)*3
        subgrid=rows[ix:ix+3, iy:iy+3].reshape(9)
        subgrids.append(subgrid)
    
    check = False
    ref = list(range(1,10))
    for r in rows:
        check = sorted(r) == ref
        if not check: return False

    for c in columns:
        check = sorted(c) == ref
        if not check: return False

    for sg in subgrids:
        check = sorted(sg) == ref
        if not check: return False
    
    return True

def init(context):
    scene = context.scene
    bd = scene.Sudoku_board
    level = scene.Sudiku_level
    bd.clear()
    
    slt = solution_board()
    pzl = puzzel_board(slt, level_dict[level])
    
    for s_line, p_line in zip(slt, pzl):
        for s, p in zip(s_line, p_line):
            item = bd.add()
            item.puzzel_number = p
            item.solution_number = s
            item.input_number = p
    
    scene.Sudoku_active = 0
    
class SUDOKU_OT_set_active(bpy.types.Operator):
    bl_idname = 'sudoku.set_active'
    bl_label = 'Set Active'
    bl_options = {'UNDO'}
    
    index: bpy.props.IntProperty(name='index', default=0)
    
    def execute(self, context):
        scene = context.scene
        bd = scene.Sudoku_board
        
        for item in bd:
            item.select=False
        bd[self.index].select=True
        
        scene.Sudoku_active = self.index
        
        return {'FINISHED'}

class SUDOKU_OT_set_number(bpy.types.Operator):
    bl_idname = 'sudoku.set_number'
    bl_label = 'Set Number'
    bl_options = {'UNDO'}
    
    number: bpy.props.IntProperty(name='number', default=1)
    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        index = scene.Sudoku_active
        return scene.Sudoku_board[index].puzzel_number==0
    
    def execute(self, context):
        scene = context.scene
        index = scene.Sudoku_active
        
        scene.Sudoku_board[index].input_number = self.number
        
        return {'FINISHED'}


class SUDOKU_OT_reset(bpy.types.Operator):
    bl_idname = 'sudoku.reset'
    bl_label = 'Reset'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        
        for item in scene.Sudoku_board:
            item.input_number = item.puzzel_number
        
        return {'FINISHED'}

class SUDOKU_OT_fill_solution(bpy.types.Operator):
    bl_idname = 'sudoku.fill_solution'
    bl_label = 'Fill Solution'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        
        for item in scene.Sudoku_board:
            item.input_number = item.solution_number
        
        return {'FINISHED'}

class SUDOKU_OT_randomize(bpy.types.Operator):
    bl_idname = 'sudoku.randomize'
    bl_label = 'Randomize'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        init(context)
        return {'FINISHED'}

# 0,1,2 = 0
# 3,4,5 = 3
# 6,7,8 = 6

# [0:3, 0:3], [0:3, 3:6], [0:3, 6:9]
# [3:6, 0:3], [3:6, 3:6], [3:6, 6:9]
# [6:9, 0:3], [6:9, 3:6], [6:9, 6:9]

class SUDOKU_OT_submit(bpy.types.Operator):
    bl_idname = 'sudoku.submit'
    bl_label = 'Submit'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        if check(context):
            scene.Sudoku_state = 'End'
        else:
            self.report({'ERROR'}, 'Puzzel Unsolved !')
        return {'FINISHED'}

class SUDOKU_OT_play(bpy.types.Operator):
    bl_idname = 'sudoku.play'
    bl_label = 'Play'
    bl_options = {'UNDO'}

    level: bpy.props.EnumProperty(items = levels)
    
    def execute(self, context):
        scene = context.scene
        
        scene.Sudoku_active = 0
        scene.Sudiku_level = self.level
        
        init(context)
        
        scene.Sudoku_state = 'Play'
        
        return {'FINISHED'}

class SUDOKU_OT_set_state(bpy.types.Operator):
    bl_idname = 'sudoku.set_state'
    bl_label = 'Set State'
    bl_options = {'UNDO'}
    
    state: bpy.props.EnumProperty(items=states)
    
    def execute(self, context):
        scene = context.scene
        scene.Sudoku_state = self.state
        return {'FINISHED'}


class SUDOKU_PT_main_panel(bpy.types.Panel):
    """sudoku main panel"""
    bl_category = "Sudoku"
    bl_label = "Sudoku"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    @classmethod
    def poll(cls, context):
        return context.area.ui_type == 'VIEW_3D'
    
    def draw(self, context):
        scene = context.scene
        if scene.Sudoku_state == 'Start':
            draw_start(self, context)
        elif scene.Sudoku_state == 'Play':
            draw_play(self, context)
        elif scene.Sudoku_state == 'End':
            draw_end(self, context)
        

class Board(bpy.types.PropertyGroup):
    puzzel_number: bpy.props.IntProperty(default=0, soft_min=1, min=0, max=9)
    solution_number: bpy.props.IntProperty(default=0, soft_min=1, min=0, max=9)
    input_number: bpy.props.IntProperty(default=0, soft_min=1, min=0, max=9)
    
    select: bpy.props.BoolProperty(default=False)

classes=[
    Board,
    
    SUDOKU_OT_set_number,
    SUDOKU_OT_set_active,
    SUDOKU_OT_reset,
    SUDOKU_OT_fill_solution,
    SUDOKU_OT_randomize,
    SUDOKU_OT_submit,
    SUDOKU_OT_play,
    SUDOKU_OT_set_state,
    
    SUDOKU_PT_main_panel,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    
    bpy.types.Scene.Sudoku_board = bpy.props.CollectionProperty(type = Board)
    bpy.types.Scene.Sudoku_active = bpy.props.IntProperty(default=0)
    
    bpy.types.Scene.Sudiku_level = bpy.props.EnumProperty(name = 'Level',items=levels, default = 'Easy')
    bpy.types.Scene.Sudoku_state = bpy.props.EnumProperty(name = 'State',items=states, default = 'Start')
#    init()

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    
    del bpy.types.Scene.Sudoku_board
    del bpy.types.Scene.Sudoku_active
    
    del bpy.types.Scene.Sudiku_level
    del bpy.types.Scene.Sudoku_state


if __name__ == "__main__":
    register()

