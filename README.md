# Centralized Blockchain, TP1: Concurrencia y Comunicaciones, Sistemas Distribuidos I (75.74), FIUBA

## Modo de uso

### Servidores
Levantar los servidores de la blockchain

```bash
docker-compose up
```

Para eliminar los containers de docker creados y los archivos generados por los servidores:

```bash
./docker-compose-down.sh
```

Configuraciones de despliegue, configurables desde `docker-compose.yaml`:
* `STORAGE_MANAGER_WRITE_PORT`: Puerto de funcionamiento del servicio que permite persistir blocks.
* `STORAGE_MANAGER_READ_PORT`: Puerto de funcionamiento del servicio que permite obtener blocks de la blockchain.
* `READ_PROCESS_AMOUNT`: Cantidad de procesos que forman el `pool` de procesos que responde request para obtener blocks de la blockchain.
* `STORAGE_MANAGER_MINED_PER_MINUTE_PORT`: Puerto de funcionamiento del servicio que permite obtener blocks minados en un minuto.
* `MINED_PER_MINUTE_PROCESS_AMOUNT`: Cantidad de procesos que forman el `pool` de procesos que responde request para obtener blocks minados en un minuto.
* `BLOCK_BUILDER_PORT`: Puerto de funcionamiento del servicio que permite agregar chunks a la blockchain.
* `MAX_BLOCKS_ENQUEUED`: Cantidad máxima de bloques encolados para ser minados. Una vez esta cantidad se supere, el servicio para agregar bloques a la blockchain comenzara a responder `SERVICE_UNAVAILABLE_RESPONSE_CODE`.
* `MINERS_AMOUNT`: Cantidad de miners a utilizar, los miners son quienes intentan resolver el desafio criptografico para agregar un bloque a la blockchain.
* `MINED_COUNTER_PORT`: Puerto de funcionamiento del servicio que permite agregar chunks a la blockchain obtener información sobre los bloques minados por cada miner.
* `GET_MINED_PER_MINER_PROCESS_AMOUNT`: Cantidad de procesos que forman el `pool` de procesos que responde request para obtener cantidad blocks minados por cada miner.


### Clientes

Para cada uno de las funcionalidades provistas a los usuarios encontraremos un cliente distinto. Estos son archivos `.sh` que se encuentran en la carpeta `client/`. Los mismos son:

* `add_chunk.sh`: Permite a los usuarios agregar un chunk a la blockchain.
* `get_block.sh`: Permite obtener un bloque de la blockchain junto a sus entries.
* `get_mined_per_miner.sh`: Permite obtener información acerca de los minados realizado por cada uno de los `miners`.
* `get_mined_per_minute.sh`: Permite obtener los bloques agregados a la blockchain en un minuto especificado.

Para mas información acerca de cada uno de estos comandos usar:

```bash
cd client/
./add_chunk.sh --help
./get_block.sh --help
./get_mined_per_miner.sh --help
./get_mined_per_minute.sh --help
```

## Brief summary Blockchain

* Estructura de datos: Lista enlazada donde cada bloque tiene un header y un payload. A cada nodo se le aplica una función de hash que identifica al bloque. Esta función de hash también toma como parámetro el hash del bloque previo (de aca proviene la integridad).
* Minado: Minar es la operación de agregar un bloque a la blockchain. Para ello un worker debe generar un bloque cuyo hash sea menor a cierto número. Mientras menor sea el número, más difícil es minar un bloque. El trabajo de cada minero es generar un bloque que cumpla con dicha condición, para ello se le concatena un nonce al bloque y se hashea el conjunto. En cada iteración el worker va incrementando el nonce hasta que se cumpla la condición.

## Requerimientos funcionales
Se solicita un sistema distribuido que brinde la funcionalidad de una blockchain. Los usuarios deben ser capaces de almacenar un chunk de datos en la blockchain. Los chunks que envían los usuarios se batchean en un bloque que será almacenado en la blockchain. Un bloque está compuesto a lo sumo de M chunks. La máxima cantidad de chunks por bloque (M) es de 256 (especificado en el formato de bloque propuesto como entries_amount). El tamaño de cada chunk no puede superar los 65536 bytes. Un hash es considerado válido en la blockchain si el hash sha256 del bloque es menor a cierto número. Este número se calcula como: (2^256) / difficulty. La dificultad se almacena junto al bloque y es calculada dinámicamente. Cada 256 bloques minados se ajusta la dificultad según la ecuación: difficulty = prev_difficulty * (12s / (ELAPSED_TIME / 256)).

El sistema debe proveer la siguiente interfaz/contrato:
* Almacenar un chunk de datos en la blockchain
* Obtener un bloque de la blockchain
* Obtener los bloques minados dado un intervalo de 1 minuto
* Obtener cantidad de bloques minados de forma exitosa y errónea por
cada miner

## Requerimientos no funcionales

Se espera una cantidad masiva de lecturas de los bloques de la blockchain y una gran cantidad de escrituras a la misma de distintos usuarios. El sistema debe estar preparado para coordinar múltiples workers con el objetivo de aumentar las chances de minar un bloque. El sistema debe estar optimizado para lecturas de bloques Por cuestiones de auditoría, la blockchain debe ser almacenada y accedida desde un único nodo aislado del resto del sistema y accedido a través de la red por un protocolo definido por el usuario. Se espera que el sistema se encuentre disponible en todo momento,
permitiendo que descarte bloques en caso de no poder procesarlos. No está permitido almacenar todos los bloques en un único archivo
