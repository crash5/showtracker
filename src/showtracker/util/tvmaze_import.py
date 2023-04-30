import sys
import showtracker.sqliteapi as db

from . import tvmaze as tvm


def import_series(to_import):
    print(f'Import series: {to_import}')
    for maze_id in to_import:
        try:
            show = tvm.get_show_from_maze(maze_id)
            print(show)
            episodes = tvm.get_episodes_from_maze(maze_id)
            print(f'episode count: {len(episodes)}')
            show.episodes = episodes
        except Exception as e:
            print(f'Error during fetch {maze_id}: {e}')
            continue

        print(f'Save show with mazeid {maze_id} to DB')
        show_id = tvm.save(show)
        print(f'Save show with id {show_id} to User')
        db.save_show_to_user(show_id, 1, 1, 1)


if __name__ == '__main__':
    print('begin')

    import_series(set(sys.argv[1:]))

    print('end')
