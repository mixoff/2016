CC=gcc
CFLAGS=-I./ -I $(SDK_DIR)/usr/include
LDFLAGS=-L$(SDK_DIR)/usr/lib -larcontroller -larnetwork -larstream2 -larsal -larcommands -larnetworkal -lardiscovery -larstream -ljson

SDK_DIR=/home/mrnoda/Dev/mixoff/drone/arsdk3
EXEC_BIN=bin/drone
FIFO_FILE=bin/fifo

_OBJECTS=BebopFifoStream.o
OBJECTS=$(patsubst %,obj/%,$(_OBJECTS))

all: $(EXEC_BIN)

obj/%.o: src/%.c
	mkdir -p obj
	$(CC) -c -o $@ $< $(CFLAGS)

$(EXEC_BIN): $(OBJECTS)
	mkdir -p bin
	$(CC) -o $@ $^ $(CFLAGS) $(LDFLAGS)

.PHONY: clean

clean:
	rm -rf obj/* bin/*

clean_fifo:
	rm -rf ${FIFO_FILE}

run: ${EXEC_BIN} clean_fifo
	$(SDK_DIR)/native-wrapper.sh $(EXEC_BIN) ${FIFO_FILE}
