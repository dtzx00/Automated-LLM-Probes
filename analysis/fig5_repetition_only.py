"""Repetition-based uniqueness alone (no DAT reference), by model release date."""
from overtime_style import *
BTW_LABEL='Human uniqueness'
dat,ch,H_DAT,H_CH,models=load_churn(); xmin,xmax=limits(dat,models)
fig,ax=new_fig()
lineages(ax,dat,ch,models,'between')
human_lines(ax,xmin,xmax,H_DAT,H_CH,show_dat=False,show_btw=True,btw_label_x=2023.02)
between_markers(ax,dat,ch,models)
frame(ax,xmin,xmax,"Uniqueness by Model Release Date\n"
                   "Rarity of a response's words within its own population, on the DAT scale; purple dotted = human",ylim=CHURN_YLIM)
legend(ax,dat,models,[Line2D([0],[0],marker='o',ls='none',markerfacecolor='white',markeredgecolor='#555',
                             markeredgewidth=2.6,ms=12,label='Uniqueness'),
                      Line2D([0],[0],color=HUMAN_PURPLE,lw=3,ls=':',marker='o',ms=12,label='Human')],
       open_style=True)
save(fig,"fig5_repetition_only.png")
