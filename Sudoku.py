# sudoku puzzel generator from
# https://stackoverflow.com/questions/45471152/how-to-create-a-sudoku-puzzle-in-python
# author Alain T.
# license under CC BY-SA 4.0, competible with GPL v3
# slightly modified
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


# sudoku solver from
# https://stackoverflow.com/questions/1697334/algorithm-for-solving-sudoku?answertab=active#tab-top
# author Ahmed4end
# license under CC BY-SA 4.0, competible with GPL v3
def solver(board):
    empties = [(i,j) for i in range(9) for j in range(9) if board[i][j] == 0]
    predict = lambda i, j: set(range(1,10))-set([board[i][j]])-set([board[y+range(1,10,3)[i//3]][x+range(1,10,3)[j//3]] for y in (-1,0,1) for x in (-1,0,1)])-set(board[i])-set(list(zip(*board))[j])
    if len(empties)==0:
        return True
    gap = next(iter(empties))
    predictions = predict(*gap)
    for i in predictions:
        board[gap[0]][gap[1]] = i
        if solver(board):
            return True
        board[gap[0]][gap[1]] = 0
    return False



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

bl_info = {
    "name": "Sudoku",
    "author": "Latidoremi",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "N Panel > Sudoku",
    "description": "Sudoku Game",
    "category": "Games",
}

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

contexts=[
    ('Start','Start','',0),
    ('Play','Play','',1),
    ('End','End','',2),
    ('Solver','Solver','',3),
]

def draw_input(layout):
    row = layout.row(align = True)
    for i in range(10):
        op = row.operator('sudoku.set_number',text = (str(i) if i!=0 else ''))
        op.number = i

def draw_start(self, context):
    layout = self.layout
    scene = context.scene
    if scene.Sudoku_play_board:
        layout.operator('sudoku.set_context', text='Resume').context = 'Play'
    
    col = layout.column(align=True)
    col.operator('sudoku.play', text = 'Easy').level = 'Easy'
    col.operator('sudoku.play', text = 'Normal').level = 'Normal'
    col.operator('sudoku.play', text = 'Hard').level = 'Hard'
    col.operator('sudoku.play', text = 'Insane').level = 'Insane' 
    
    layout.operator('sudoku.set_context', text='Solver').context = 'Solver'

def draw_play(self, context):
    layout = self.layout
    scene = context.scene
    board = scene.Sudoku_play_board
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
                op_text = str(item.puzzel_number)+'\''
        else:
            if item.input_number==board[active_index].input_number:
                op_text = ('['+str(item.input_number)+']' if item.input_number!=0 else '')
            else:
                op_text = (str(item.input_number) if item.input_number!=0 else '')
          
        row.operator('sudoku.set_active', text=op_text, depress=(active_index==i)).index = i

    draw_input(layout)
    
    layout.operator('sudoku.submit', icon='CHECKMARK')
    row = layout.column(align = True)
    row.operator('sudoku.reset', icon='FILE_REFRESH')
    row.operator('sudoku.randomize', icon= 'RNDCURVE')
    row.operator('sudoku.set_context', text='Quit', icon= 'LOOP_BACK').context='Start'
    
def draw_end(self, context):
    layout = self.layout
    scene = context.scene
    board = scene.Sudoku_play_board
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
    row.operator('sudoku.set_context', text='!!! You Win !!!',emboss=False).context='Start'

def draw_solver(self, context):
    layout = self.layout
    scene = context.scene
    board = scene.Sudoku_solver_board
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
            op_text = str(item.solution_number)+'\''
        else:
            op_text = (str(item.solution_number) if item.solution_number!=0 else '')

        row.operator('sudoku.set_active', text=op_text, depress=(active_index==i)).index = i
    
    draw_input(layout)
    
    layout.operator('sudoku.solve', text='Solve',icon='CHECKMARK')
    col = layout.column(align=True)
    col.operator('sudoku.reset', text='Reset',icon='FILE_REFRESH')
    col.operator('sudoku.clear', text='Clear',icon='TRASH')
    col.operator('sudoku.set_context', text='Quit', icon='LOOP_BACK').context = 'Start'
    pass

# 0,1,2 = 0
# 3,4,5 = 3
# 6,7,8 = 6

# [0:3, 0:3], [0:3, 3:6], [0:3, 6:9]
# [3:6, 0:3], [3:6, 3:6], [3:6, 6:9]
# [6:9, 0:3], [6:9, 3:6], [6:9, 6:9]

def check(context):
    scene = context.scene
    inputs = [item.input_number for item in scene.Sudoku_play_board]
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
    bd = scene.Sudoku_play_board
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

def init_solver_board(context):
    scene = context.scene
    bd = scene.Sudoku_solver_board
    
    if bd:
        return
    
    bd.clear()
    for i in range(81):
        item = bd.add()

class SUDOKU_OT_set_context(bpy.types.Operator):
    bl_idname = 'sudoku.set_context'
    bl_label = 'Set context'
    bl_options = {'UNDO'}
    
    context: bpy.props.EnumProperty(items=contexts)
    
    def execute(self, context):
        scene = context.scene
        scene.Sudoku_context = self.context
        if self.context == 'Solver':
            init_solver_board(context)
        return {'FINISHED'}

class SUDOKU_OT_set_active(bpy.types.Operator):
    bl_idname = 'sudoku.set_active'
    bl_label = 'Set Active'
    bl_options = {'UNDO'}
    
    index: bpy.props.IntProperty(name='index', default=0)
    
    def execute(self, context):
        scene = context.scene
        if scene.Sudoku_context == 'Play':
            bd = scene.Sudoku_play_board
        elif scene.Sudoku_context == 'Solver':
            bd = scene.Sudoku_solver_board
        
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
        if scene.Sudoku_context == 'Play':
            return scene.Sudoku_play_board[index].puzzel_number==0
        elif scene.Sudoku_context == 'Solver':
            return True
    
    def execute(self, context):
        scene = context.scene
        index = scene.Sudoku_active
        
        if scene.Sudoku_context == 'Play':
            scene.Sudoku_play_board[index].input_number = self.number
        elif scene.Sudoku_context == 'Solver':
            scene.Sudoku_solver_board[index].puzzel_number = self.number
            scene.Sudoku_solver_board[index].solution_number = self.number
            
        return {'FINISHED'}

class SUDOKU_OT_reset(bpy.types.Operator):
    bl_idname = 'sudoku.reset'
    bl_label = 'Reset'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        
        if scene.Sudoku_context == 'Play':
            for item in scene.Sudoku_play_board:
                item.input_number = item.puzzel_number
        elif scene.Sudoku_context == 'Solver':
            for item in scene.Sudoku_solver_board:
                item.solution_number = item.puzzel_number
        
        return {'FINISHED'}

class SUDOKU_OT_fill_solution(bpy.types.Operator):
    bl_idname = 'sudoku.fill_solution'
    bl_label = 'Fill Solution'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        
        for item in scene.Sudoku_play_board:
            item.input_number = item.solution_number
        
        return {'FINISHED'}

class SUDOKU_OT_randomize(bpy.types.Operator):
    bl_idname = 'sudoku.randomize'
    bl_label = 'Randomize'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        init(context)
        return {'FINISHED'}

class SUDOKU_OT_submit(bpy.types.Operator):
    bl_idname = 'sudoku.submit'
    bl_label = 'Submit'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        if check(context):
            scene.Sudoku_context = 'End'
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
        
        scene.Sudoku_context = 'Play'
        
        return {'FINISHED'}

class SUDOKU_OT_solve(bpy.types.Operator):
    bl_idname = 'sudoku.solve'
    bl_label = 'Solve'
    bl_options = {'UNDO'}

    def execute(self, context):
        scene = context.scene
        bd = scene.Sudoku_solver_board
        puzzel = np.array([item.puzzel_number for item in bd]).reshape((9,9))
        
        solved = deepcopy(puzzel)
        solver(solved)
        
        solved = [n for row in solved for n in row]
        for item, n in zip(bd, solved):
            item.solution_number = n
        
        return {'FINISHED'}

class SUDOKU_OT_clear(bpy.types.Operator):
    bl_idname = 'sudoku.clear'
    bl_label = 'Clear'
    bl_options = {'UNDO'}

    def execute(self, context):
        scene = context.scene
        for item in scene.Sudoku_solver_board:
            item.puzzel_number = 0
            item.solution_number =0
            
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
        if scene.Sudoku_context == 'Start':
            draw_start(self, context)
        elif scene.Sudoku_context == 'Play':
            draw_play(self, context)
        elif scene.Sudoku_context == 'End':
            draw_end(self, context)
        elif scene.Sudoku_context == 'Solver':
            draw_solver(self, context)
        

class PlayBoard(bpy.types.PropertyGroup):
    puzzel_number: bpy.props.IntProperty(default=0, soft_min=1, min=0, max=9)
    solution_number: bpy.props.IntProperty(default=0, soft_min=1, min=0, max=9)
    input_number: bpy.props.IntProperty(default=0, soft_min=1, min=0, max=9)
    
    select: bpy.props.BoolProperty(default=False)

class SolverBoard(bpy.types.PropertyGroup):
    puzzel_number: bpy.props.IntProperty(default=0, soft_min=1, min=0, max=9)
    solution_number: bpy.props.IntProperty(default=0, soft_min=1, min=0, max=9)
    
    select: bpy.props.BoolProperty(default=False)

classes=[
    PlayBoard,
    SolverBoard,
    
    SUDOKU_OT_set_context,
    SUDOKU_OT_set_active,
    SUDOKU_OT_set_number,
    SUDOKU_OT_reset,
    SUDOKU_OT_fill_solution,
    SUDOKU_OT_randomize,
    SUDOKU_OT_submit,
    SUDOKU_OT_play,
    SUDOKU_OT_solve,
    SUDOKU_OT_clear,
    
    
    SUDOKU_PT_main_panel,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    
    bpy.types.Scene.Sudoku_play_board = bpy.props.CollectionProperty(type = PlayBoard)
    bpy.types.Scene.Sudoku_active = bpy.props.IntProperty(default=0)
    
    bpy.types.Scene.Sudoku_solver_board = bpy.props.CollectionProperty(type = SolverBoard)
    
    bpy.types.Scene.Sudiku_level = bpy.props.EnumProperty(name = 'Level',items=levels, default = 'Easy')
    bpy.types.Scene.Sudoku_context = bpy.props.EnumProperty(name = 'context',items=contexts, default = 'Start')
#    init()

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    
    del bpy.types.Scene.Sudoku_play_board
    del bpy.types.Scene.Sudoku_active
    
    del bpy.types.Scene.Sudiku_level
    del bpy.types.Scene.Sudoku_context


if __name__ == "__main__":
    register()

