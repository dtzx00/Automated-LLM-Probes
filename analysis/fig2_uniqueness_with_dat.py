"""Uniqueness WITH the DAT reference, by model release date.

Uniqueness = distance from 500 HUMAN responses redrawn at random for every score.
Transparent filled markers are the model's DAT score, open markers its uniqueness, and the
arrow shows the direction of the shift between the two.
"""
from overtime_style import *
dat,uniq,H_DAT,H_UNIQ,models=load_uniq(); xmin,xmax=limits(dat,models)
fig,ax=new_fig()
lineages(ax,dat,uniq,models,'both')
human_lines(ax,xmin,xmax,H_DAT,H_UNIQ,show_dat=True,show_btw=True,dat_alpha=0.50,band=True)
shift_arrows(ax,dat,uniq,models)
dat_markers(ax,dat,models,alpha=0.50)
between_markers(ax,dat,uniq,models)
frame(ax,xmin,xmax,"From Within-Person Divergence (DAT) to Uniqueness by Model Release Date\n"
                   "Uniqueness measured against 500 human responses redrawn per score; arrow = direction of shift")
legend(ax,dat,models,[
    Line2D([0],[0],marker='o',ls='none',color='#555',alpha=0.50,ms=12,label='Within-person (DAT)'),
    Line2D([0],[0],marker='o',ls='none',markerfacecolor='white',markeredgecolor='#555',markeredgewidth=2.6,ms=12,label='Uniqueness'),
    Line2D([0],[0],color='#555',lw=2.4,alpha=0.50,label='Shift DAT to uniqueness'),
    Patch(facecolor='#555',alpha=0.10,label='Gap of scores'),
    Line2D([0],[0],color=HUMAN_PURPLE,lw=3,marker='o',ms=12,label='Human')])
save(fig,"fig2_uniqueness_with_dat.png")
