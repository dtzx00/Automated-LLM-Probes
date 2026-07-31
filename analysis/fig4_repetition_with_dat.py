"""Repetition-based uniqueness WITH the DAT reference, by model release date.

Uniqueness here = how RARE a response's words are within its own population, on the DAT scale.
Transparent filled = DAT, open = uniqueness, arrow = the drop between them.
"""
from overtime_style import *
BTW_LABEL='Human uniqueness'
dat,ch,H_DAT,H_CH,models=load_churn(); xmin,xmax=limits(dat,models)
fig,ax=new_fig()
lineages(ax,dat,ch,models,'both')
# the calibration maps human uniqueness onto the human DAT mean, so the two baselines
# coincide by construction -> draw one line, labelled for both
human_lines(ax,xmin,xmax,H_DAT,H_CH,show_dat=True,show_btw=False,dat_alpha=1.0,band=False,
            dat_label_x=2023.9,dat_label=f"Human: DAT = uniqueness = {H_DAT:.1f} (by calibration)")
shift_arrows(ax,dat,ch,models)
dat_markers(ax,dat,models,alpha=0.50)
between_markers(ax,dat,ch,models)
frame(ax,xmin,xmax,"Within-Person Divergence (DAT) and Uniqueness by Model Release Date\n"
                   "Uniqueness = rarity of a response's words within its own population, on the DAT scale",ylim=CHURN_YLIM)
legend(ax,dat,models,[
    Line2D([0],[0],marker='o',ls='none',color='#555',alpha=0.50,ms=12,label='Within-person (DAT)'),
    Line2D([0],[0],marker='o',ls='none',markerfacecolor='white',markeredgecolor='#555',markeredgewidth=2.6,ms=12,label='Uniqueness'),
    Line2D([0],[0],color='#555',lw=2.4,alpha=0.50,label='Drop DAT to uniqueness'),
    Patch(facecolor='#555',alpha=0.10,label='Gap of scores'),
    Line2D([0],[0],color=HUMAN_PURPLE,lw=3,marker='o',ms=12,label='Human')])
save(fig,"fig4_repetition_with_dat.png")
