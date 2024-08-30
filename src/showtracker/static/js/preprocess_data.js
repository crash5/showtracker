import { CustomDate } from './customdate.js';

function process_show(show) {
    let show_row = {};
    show_row.name = show.name;
    show_row.id = show.id;
    return show_row;
}

function process_episode(episode) {
    let cell = {};
    cell.name = episode.name;
    cell.seasonPadded = episode.season.toString().padStart(2, '0');
    cell.numberPadded = episode.episode.toString().padStart(2, '0');
    cell.season = episode.season;
    cell.number = episode.episode;
    const epDate = CustomDate.FromIsoString(episode.airdate);
    cell.date = epDate.dateTimeFormat();
    cell.isSeen = episode.seen;
    cell.isEpisode = true;
    cell.isAired = epDate.isOlderThan(CustomDate.Now());
    return cell;
}


export function process_airdate(data) {
    const series = data.series;
    const dateRange = Array.from(CustomDate.dateIterator(data['start_date'], data['end_date']));

    let shows = series.map(show_raw => {
        let show = process_show(show_raw);
        show.episodes = [];

        for (let date of dateRange) {
            const episode = show_raw.episodes.find(function(ep){
                return date.isSameDate(new Date(ep.airdate));
            })

            let cell = {};
            if (episode) {
                cell = process_episode(episode);
            } else {
                cell.day = date.paddedDay();
                cell.date = date.dateFormat();
                cell.isEpisode = false;
            }
            cell.isToday = date.isToday();
            cell.isWeekend = date.isWeekend();
            show.episodes.push(cell);
        }
        return show;
    });

    return shows;
}

export function process_following(data) {
    const series = data.data;

    let shows = series.map(show_raw => {
        let show = process_show(show_raw);
        show.episodes = show_raw.episodes.map(episode => process_episode(episode));
        show.season = show_raw.season;
        show.season_count = show_raw.season_count;
        return show;
    });

    return shows;
}