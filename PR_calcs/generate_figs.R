# --- IMPORT DATA : -----
Dir_dat="PR_calcs/data/"

Seattab_names=c("seats_before", 
                "Votes", 
                "Pop_vote_share", 
                "seats_after", 
                "seat_share")

Seats_2011=read.csv(paste0(Dir_dat,"2011_Nc.out"), 
                    row.names = 1, 
                    header    = FALSE,
                    sep       = "\t")
names(Seats_2011) <- Seattab_names


# ---- 2015 -----

Seats_2015=read.csv(paste0(Dir_dat,"2015_Nc.out"), 
                    row.names = 1, 
                    header    = FALSE,
                    sep       = "\t")
names(Seats_2015) <- Seattab_names

# ----  DEFINE THE COLOR PALETTE : -------

CBlQ  <- "#33FFFFFF"
CBlQt <- "#33FFFF99"

Ccon  <- "#0000CCFF"
Ccont <- "#0000CC99"

CGrn  <- "#336600FF"
CGrnt <- "#33660099"

CLib  <- "#CC0000FF"
CLibt <- "#CC000099"

CNDP  <- "#FF8000FF"
CNDPt <- "#FF800099"

Nparties=5
party_palette = c( CBlQ, CBlQt, 
                   Ccon, Ccont, 
                   CGrn, CGrnt, 
                   CLib, CLibt, 
                   CNDP, CNDPt)

cex.lab.default=1.8 
cex.axis.default=1.8 
cex.main.default=1.8
cex.default = 1.5

# --- FORMAT THE DATA FOR bargraph INPUT

SM_2011 = t( as.matrix(Seats_2011[1:Nparties,c(1,4)]) )
SM_2015 = t( as.matrix(Seats_2015[1:Nparties,c(1,4)]) )

majline_2011   = 0.5*( c( sum(Seats_2011$seats_before), 
                          sum(Seats_2011$seats_after)   ) )
Voteshare_2011 = sum(Seats_2011$seats_after)* Seats_2011$Pop_vote_share[1:Nparties] 

majline_2015 = 0.5*( c( sum(Seats_2015$seats_before), 
                        sum(Seats_2015$seats_after) ) )
Voteshare_2015 = Seats_2015$Pop_vote_share[1:Nparties]
Voteshare_2015 = sum(Seats_2015$seats_after)* Seats_2015$Pop_vote_share[1:Nparties] 

# ============ PLOT seat distribution 2011 =================

# Grouped barplot
barplot(SM_2011, 
        col=party_palette , 
        border="white", 
        font.axis=2, beside=T, 
        # legend=c("official result", "MMM projection"), 
        main = "2011 MMM seat projection",
        xlab = "Party", 
        ylab = "Seats",
        ylim = c(-1, 200 ),
        cex.lab  = cex.lab.default, 
        cex.axis = 1.6, 
        cex.main = 1.6,
        cex      = 1.5 
        )

# ---- add transparent lines for the majority threshold
lines( c(0, Nparties*3), c(majline_2011[1], majline_2011[1]), col= rgb( 0.4, 0.4, 0.4, alpha=0.3 ), lw=3 )
lines( c(0, Nparties*3), c(majline_2011[2], majline_2011[2]), col= rgb( 0.4, 0.4, 0.4, alpha=0.3 ), lw=3 )

# --- add marker lines for seat expectations under proportionality
for ( p in c(0:(Nparties-1) ) )
  {
  lines( c(1+p*3, 1+p*3+2), c( Voteshare_2011[p+1], Voteshare_2011[p+1] ),
         col= rgb( 0, 0, 0, alpha=0.8 ))
  }

# ============ seat distribution 2015 =================

barplot(SM_2015, 
        col=party_palette , 
        border="white", 
        font.axis=2, beside=T, 
        # legend=c("official result", "MMM projection"), 
        main = "2015 MMM seat projection",
        xlab = "Party", 
        ylab = "Seats",
        ylim = c(-1, 250 ),
        font.lab=2,
        cex.lab  = cex.lab.default, 
        cex.axis = 1.6, 
        cex.main = 1.6,
        cex      = 1.5 
        )

# ---- add transparent lines for the majority threshold
lines( c(0, Nparties*3), c(majline_2015[1], majline_2015[1]), col= rgb( 0.4, 0.4, 0.4, alpha=0.3 ), lw=3 )
lines( c(0, Nparties*3), c(majline_2015[2], majline_2015[2]), col= rgb( 0.4, 0.4, 0.4, alpha=0.3 ), lw=3 )

# --- add marker lines for seat expectations under proportionality
       
for ( p in c(0:(Nparties-1) ) )
{
  lines( c(1+p*3, 1+p*3+2), c( Voteshare_2015[p+1], Voteshare_2015[p+1] ),
         col= rgb( 0, 0, 0, alpha=0.8 ))
}


# ============ QUOTIENTS  =================

Quotient_names <- c("Overall_order",
                    "Party_order",
                    "Qval",
                    "const_assigned",
                    "party_ass")
Quotients_2011= read.csv( paste0(Dir_dat, "2011_qlist_Nc.out" ), 
                          sep    = "\t",
                          header = FALSE)
names(Quotients_2011) <- Quotient_names

Quotients_2015= read.csv( paste0(Dir_dat, "2015_qlist_Nc.out" ), 
                          sep    = "\t",
                          header = FALSE)
names(Quotients_2015) <- Quotient_names


# --- 2011 --- plot party quotients independently 

ymax = max( Quotients_2011[,3])
ymin = min( Quotients_2011[,3])
xmin = 0
xmax = 250
plot( Quotients_2011[Quotients_2011$party_ass=="BlQ", ][,c(2,3)],
      log="y",
      pch=1,
      xlim = c(xmin, xmax),
      ylim = c(ymin, ymax),
      col  = CBlQ,
      xlab = "j",
      ylab = expression(paste("Q" ["j"])),
      main = "Quotients by Party, 2011",
      cex.lab=1.8, 
      cex.axis=1.8, 
      cex.main=1.8,
      cex = 1.7
)
points( Quotients_2011[Quotients_2011$party_ass=="CON", ][,c(2,3)],
        pch=0,
        col = Ccon,
        cex = 1.7 
)
points( Quotients_2011[Quotients_2011$party_ass=="GRN", ][,c(2,3)],
        pch=5,
        col = CGrn,
        cex = 1.7 )
points( Quotients_2011[Quotients_2011$party_ass=="LIB", ][,c(2,3)],
        pch=2,
        col = CLib,
        cex = 1.7)
points( Quotients_2011[Quotients_2011$party_ass=="NDP", ][,c(2,3)],
        pch=6,
        col = CNDP,
        cex = 1.7)
legend( 175, ymax,
        col    = c(CBlQ, Ccon, CGrn, CLib, CNDP),
        pch    = c(1, 0, 5, 2, 6),
        legend = c("BlQ", "Con", "Grn", "Lib", "NDP"),
        cex = 1.7
)


# --- plot reordered quotients ----

ymax = max( Quotients_2011[,3])
ymin = min( Quotients_2011[,3])
xmin = 0
xmax = max ( Quotients_2011[,1])

reordered_palette = c( CBlQt, Ccont, CGrnt, CLibt, CNDPt) 
names( reordered_palette ) <- c("BlQ", "CON", "GRN", "LIB", "NDP" )
pcharracy = c(1,0,5,2,6)
names( pcharracy ) <- c("BlQ", "CON", "GRN", "LIB", "NDP" )

i=1
plot( Quotients_2011[i,c(1,3)],
      log ="y",
      pch = pcharracy[ Quotients_2011[i,5]  ],
      col = reordered_palette[ Quotients_2011[i,5]  ],
      xlim = c(xmin,xmax),
      ylim = c(ymin,ymax),
      main = "2011 Ordered Quotients",
      xlab = "i",
      ylab =  expression(paste("Q" ["i"])),
      cex.lab=1.8, 
      cex.axis=1.8, 
      cex.main=1.8,
      cex = 1.7
      )

for ( i in c( 2: dim(Quotients_2011)[1] ) )
  { points( Quotients_2011[i,c(1,3)],
        pch = pcharracy[ Quotients_2011[i,5]  ],
        col = reordered_palette[ Quotients_2011[i,5]  ],
        cex = 1.7)
}

# --- define threshold as the minimum quotient associated with seat already assigned to a constituency
thresh = min(Quotients_2011[Quotients_2011$const_assigned==1,]$Qval)
# --- and add a grey transparent line delineating this point.
lines( c(0,xmax),c(thresh,thresh), col= rgb( 0.4, 0.4, 0.4, alpha=0.3 ), lw=3 )
legend( 450, ymax,
        col    = c(CBlQ, Ccon, CGrn, CLib, CNDP),
        pch    = c(1, 0, 5, 2, 6),
        legend = c("BlQ", "Con", "Grn", "Lib", "NDP"),
        cex = 1.7
)

# --- 2015 ----

ymax = max( Quotients_2015[,3])
ymin = min( Quotients_2015[,3])
xmin = 0
xmax = max ( Quotients_2015[,2])
plot( Quotients_2015[Quotients_2015$party_ass=="BlQ", ][,c(2,3)],
      log="y",
      pch=1,
      xlim = c(xmin, xmax),
      ylim = c(ymin, ymax),
      col  = CBlQ,
      xlab = "j",
      ylab = expression(paste("Q" ["j"])),
      main = "Quotients 2015",
      cex.lab=2.2, 
      cex.axis=2.2, 
      cex.main=2.4,
      cex = 2.2
)
points( Quotients_2015[Quotients_2015$party_ass=="CON", ][,c(2,3)],
        pch=0,
        col = Ccon,
        cex = 1.7
)
points( Quotients_2015[Quotients_2015$party_ass=="GRN", ][,c(2,3)],
        pch=5,
        col = CGrn,
        cex = 1.7
        )
points( Quotients_2015[Quotients_2015$party_ass=="LIB", ][,c(2,3)],
        pch=2,
        col = CLib,
        cex = 1.7
        )
points( Quotients_2015[Quotients_2015$party_ass=="NDP", ][,c(2,3)],
        pch=6,
        col = CNDP,
        cex = 1.7
        )
legend( 155, ymax,
        col    = c(CBlQ, Ccon, CGrn, CLib, CNDP),
        pch    = c(1, 0, 5, 2, 6),
        legend = c("BlQ", "Con", "Grn", "Lib", "NDP"),
        cex = 1.2
)

ytick    <-c(  1E4,   5E4,   1E5,   5E5,   1E6, 5E6  );
yticklab <-c("1E4", "5E4", "1E5", "5E5", "1E6", "5E6");
axis(side=2, at=ytick, labels = yticklab)

Quotients_2015_sorted = sort( Quotients_2015$Qval, decreasing = TRUE)
cutoff_without_constituency = Quotients_2015_sorted [338]

lines(c(0,300),c(cutoff_without_constituency,cutoff_without_constituency), col = rgb(0,0,0,alpha=0.5), lw = 5 )


# --- plot reordered quotients ----

ymax = max( Quotients_2015[,3])
ymin = min( Quotients_2015[,3])
xmin = 0
xmax = max ( Quotients_2015[,1])

reordered_palette = c( CBlQt, Ccont, CGrnt, CLibt, CNDPt) 
names( reordered_palette ) <- c("BlQ", "CON", "GRN", "LIB", "NDP" )
pcharracy = c(1,0,5,2,6)
names( pcharracy ) <- c("BlQ", "CON", "GRN", "LIB", "NDP" )

i=1
plot( Quotients_2015[i,c(1,3)],
      log  = "y",
      pch  = pcharracy[ Quotients_2015[i,5]  ],
      col  = reordered_palette[ Quotients_2015[i,5]  ],
      xlim = c(xmin,xmax),
      ylim = c(ymin,ymax),
      main = "2015 Ordered Quotients",
      xlab = "i",
      ylab =  expression(paste("Q" ["i"])),
      cex.lab=1.8, 
      cex.axis=1.8, 
      cex.main=1.8,
      cex = 1.7
)

for ( i in c( 2: dim(Quotients_2015)[1] ) )
{ points( Quotients_2015[i,c(1,3)],
          pch = pcharracy[ Quotients_2015[i,5]  ],
          col = reordered_palette[ Quotients_2015[i,5]  ],
          cex = 1.7 
          )
}

# --- define threshold as the minimum quotient associated with seat already assigned to a constituency
thresh = min(Quotients_2015[Quotients_2015$const_assigned==1,]$Qval)
# --- and add a grey transparent line delineating this point.
lines( c(0,xmax),c(thresh,thresh), col= rgb( 0.4, 0.4, 0.4, alpha=0.3 ), lw=5 )
legend( 500, ymax,
        col    = c(CBlQ, Ccon, CGrn, CLib, CNDP),
        pch    = c(1, 0, 5, 2, 6),
        legend = c("BlQ", "Con", "Grn", "Lib", "NDP"),
        cex = 1.7 
)

