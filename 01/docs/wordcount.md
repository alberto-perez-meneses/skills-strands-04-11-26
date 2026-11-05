# wordcount

Agente de un solo turno que cuenta una letra, escribe el resultado en un archivo y lo muestra con `cat`.

Código: [`src/wordcount/app.py`](../src/wordcount/app.py).

## Descripción

El agente decide, en un solo turno, cuántas erres hay en una palabra, guarda el número en un archivo y lo muestra con un comando de shell.

## Temas

- Agente de Strands: modelo más tools, con el bucle de llamadas incluido.
- Tool declarativa: `@tool` publica la función; el esquema sale de la firma y del docstring.
- Validación de argumentos: `letter_counter` rechaza una letra que no sea un solo carácter.
- Proveedor de modelo separado del agente: aquí es Ollama (`llama3.1`).
- Tools que vienen con el SDK: editar archivos y ejecutar un comando.

## Pieza de código

La tool propia está en `letter_counter`. El docstring es el contrato que ve el modelo:

```8:23:01/src/wordcount/app.py
@tool
def letter_counter(word: str, letter: str) -> int:
    """
    Count occurrences of a specific letter in a word.

    Args:
        word (str): The input word to search in
        letter (str): The specific letter to count

    Returns:
        int: The number of occurrences of the letter in the word
    """
    if len(letter) != 1:
        raise ValueError("The 'letter' parameter must be a single character")

    return word.lower().count(letter.lower())
```

El modelo se construye aparte y el agente solo lo recibe, junto con la lista de tools:

```26:31:01/src/wordcount/app.py
model = OllamaModel(
    host=os.environ.get("OLLAMA_HOST", "http://ollama:11434"),
    model_id="llama3.1",
)
agent = Agent(model=model,
tools=[letter_counter, file_editor, shell])
```

La última línea lanza el bucle una vez, con un prompt fijo. Cuando esa llamada vuelve, el proceso termina:

```34:34:01/src/wordcount/app.py
agent(f'How many letter R\'s are in the word "strawberry"? Write the answer to answer_{timestamp}.txt. then pause for two seconds. then run "cat answer_{timestamp}.txt" to see the result.')
```

`sleep` está importada al inicio del archivo. El prompt pide una pausa de dos segundos. Esa función no aparece en la lista `tools` del `Agent`.

## Qué usa

- Modelo `llama3.1` en Ollama (`OLLAMA_HOST`, por defecto `http://ollama:11434`).
- Tool propia `letter_counter(word, letter)`. Si `letter` no es un solo carácter, lanza `ValueError`.
- Tools incluidas con el SDK: `file_editor` y `shell`.
- Prompt fijo: cuenta las erres de `"strawberry"`, escribe `answer_<fecha>.txt` y ejecuta `cat` sobre ese archivo.

`sleep` está importada. El prompt pide una pausa de dos segundos. Esa tool no está en la lista que recibe el agente.

## Activar

En [`entrypoint.sh`](../entrypoint.sh):

```sh
python src/wordcount/app.py
```

Desde la raíz de `ejercicios`:

```powershell
docker compose up --build app
```

## Qué esperar

El proceso no abre el puerto 8000. Cuando el agente termina, el contenedor se detiene. La traza sale en los logs:

```powershell
docker compose logs app
```

El archivo `answer_<fecha>.txt` queda en el directorio de trabajo del contenedor (`/app`). No hay un volumen montado para la app, así que ese archivo desaparece al recrear el contenedor.
