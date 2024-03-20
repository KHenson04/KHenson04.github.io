# IK FK Builder Script

A Maya Python tool that automates IK FK building

# IK FK Rig Call
To call the script, copy the python code below and the IK FK UI will appear:
``` python
import KirstenTools as KT
import imp
imp.reload (KT)


def buttonAction(args):
    curSel = cmds.ls(selection = True)
    if len(curSel) >= 3:
        bindJoints  = curSel[:3]
        optionCurve = curSel[3] if len(curSel) >3 else None
        KT.IkFkRig.makeFingerRig( bindJoints = bindJoints, 
                                  optionCurve = optionCurve )
                                  
def showUI():
  win = cmds.window(title="IK_FK_Builder", widthHeight = (200,200))
  cmds.columnLayout()
  cmds.text(label=" Select 3 joints and press 'Build' to create rig!")
  cmds.button(label="IK_FK_Build", command = buttonAction)
  cmds.showWindow(win)
  
showUI()

```

# IK FK Builder
This function automates the process of creating an IK/FK Chain for rigging in Maya! It takes a list of three joints
representing the finger, arm, or any three hierarchy joints and generates IK / FK controls. Users can specify various parameters
such as the option curve, control sizes, and colors to customize the rig according to fit their needs:
## Parameters:
- bindJoints (list): A list of joint names representing the joints.
- optionCurve (str, optional): Name of the option curve. Defaults to None.
- poleVectorPreset (str, optional): Preset for the pole vector curve. Defaults to Curve.PRESET_TRIANGLE.
- ikControlPreset (str, optional): Preset for the IK control curve. Defaults to Curve.PRESET_TRIANGLE.
- fkControlPreset (str, optional): Preset for the FK control curve. Defaults to Curve.PRESET_SQUARE.
- controlSize (float, optional): Size of the control curves. Defaults to 1.
- fkControlColor (tuple, optional): RGB color for the FK control curve. Defaults to Curve.RED.
- ikControlColor (tuple, optional): RGB color for the IK control curve. Defaults to Curve.BLUE

# Curve Tool
The curve tool is a script that lets users customize the typr of curves used in the tool: 
  - Parameters: name, type, size, and parent

