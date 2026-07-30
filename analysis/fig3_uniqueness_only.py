"""Uniqueness alone (no DAT reference), by model release date.

Uniqueness = distance from a position-agnostic, HUMAN-ONLY reference pool.
"""
from overtime_style import *
dat,uniq,H_DAT,H_UNIQ,models=load_uniq(); xmin,xmax=limits(dat,models)
fig,ax=new_fig()
lineages(ax,dat,uniq,models,'between')
human_lines(ax,xmin,xmax,H_DAT,H_UNIQ,show_dat=False,show_btw=True)
between_markers(ax,dat,uniq,models)
frame(ax,xmin,xmax,"Uniqueness by Model Release Date\n"
                   "Distance from a human-only, position-agnostic reference; purple dotted = human baseline; lines = OpenAI and Claude")
legend(ax,dat,models,[Line2D([0],[0],marker='o',ls='none',markerfacecolor='white',markeredgecolor='#555',
                             markeredgewidth=2.6,ms=12,label='Uniqueness'),
                      Line2D([0],[0],color=HUMAN_PURPLE,lw=3,ls=':',marker='o',ms=12,label='Human')],
       open_style=True)
save(fig,"/home/user/fig3_uniqueness_only.png")
