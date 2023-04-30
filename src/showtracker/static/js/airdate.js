import { handle_status_change } from './operations.js';
import { process_airdate } from './preprocess_data.js';

export function populate_airdates(data, airdate_table) {
    const processed_data = process_airdate(data);

    processed_data.forEach(function(show) {
        const show_row = airdate_table.insertRow();
        const first_cell = show_row.insertCell();
        first_cell.innerHTML = `<a href="/series/${show.id}">${show.name}</a>`;
        first_cell.classList.add("airdate-showname");

        show.episodes.forEach(function(episode) {
            const cell = show_row.insertCell();

            if (!episode.isEpisode) {
                cell.innerHTML = `<sup>${episode.day}</sup><br>&nbsp;`;
                cell.title = episode.date;
                if (episode.isToday) {
                	cell.classList.add("airdate-today");
                } else if (episode.isWeekend) {
                	cell.classList.add("airdate-weekend");
                }
            } else {
                cell.innerHTML = `${episode.seasonPadded}<br>${episode.numberPadded}`;
                cell.title = `${episode.name}\n${episode.seasonPadded}x${episode.numberPadded}\n${episode.date}`;
                cell.classList.add("airdate-episode");
                if (episode.isSeen) {
                    cell.classList.add("airdate-episode-seen");
                } else if (episode.isAired) {
                    cell.classList.add("airdate-episode-aired");
                }
                if (episode.isToday) {
                    first_cell.classList.add("airdate-showname-episode-today");
                }
                cell.onclick = function() { handle_status_change(data.user_id, show.id, episode.season, episode.number, cell); };
            }
        });
    });
}