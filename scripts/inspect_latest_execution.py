from pathlib import Path

from app.recorder.event_parser import EventParser


def main() -> None:
    executions_folder = Path("data") / "executions"
    print("Buscando ejecuciones en:", executions_folder)

    executions = sorted(executions_folder.glob("execution_*"))
    print("Ejecuciones encontradas:", len(executions))

    if not executions:
        print("No existen ejecuciones.")
        return

    execution_folder = executions[-1]
    actions_file = execution_folder / "actions.json"
    output_file = execution_folder / "qa_actions.json"

    print("Ejecución:", execution_folder)
    print("Entrada:", actions_file)
    print("¿Existe actions.json?:", actions_file.exists())

    qa_actions = EventParser().parse_file(actions_file, output_file)
    print("Acciones QA:", len(qa_actions))

    for action in qa_actions:
        print(f"{action['sequence']}. {action['description']}")

    print("Archivo generado:", output_file)


if __name__ == "__main__":
    main()