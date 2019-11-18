#IDIR =/usr/include/
CC=g++
CFLAGS  =  -ggdb -I/sw/include -I/Users/lana/Desktop/Science/Code_library/
LDFLAGS =  
# library files aren't showing up from homebrew with   -L/sw/lib -lgsl -lm -lgslcblas.
# Don't need them for this project anyway, but should resolve this in general

DEPS =  
OBJ  = PR_MMM.obj 

%.obj: %.cpp $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

PR_MMM.x: $(OBJ)
	g++ -o $@ $^ $(LDFLAGS)

#void_numerics.db: $(OBJ)
#	g++ -g -o $@ $^ $(LDFLAGS)

ALL_OBJS = PR_MMM.obj  
clean:
	$(RM) $(ALL_OBJS)

debug:
	g++ -ggdb PR_MMM.cpp  $(LDFLAGS) -I/opt/local/include



