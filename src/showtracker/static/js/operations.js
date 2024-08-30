async function set_status(member_id, series_id, season, number, status) {
    const url = `/api/users/${member_id}/series/${series_id}/seasons/${season}/episodes/${number}`;
    const body = {"status": status};
    const response = await fetch(url, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
    });
    return response;
}

export async function handle_status_change(member_id, series_id, season, number, cell) {
    let status = 'seen';
    if (cell.classList.contains('airdate-episode-seen')) {
        status = 'unseen';
    }
    set_status(member_id, series_id, season, number, status)
        .then(result => {
            if (result.status == 200) {
                cell.classList.toggle("airdate-episode-seen");
            } else {
                console.log(`${result.status} - ${result.statusText}`);
            }
        })
        .catch(err => { console.log(err.message) }
    );
}