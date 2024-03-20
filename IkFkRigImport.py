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