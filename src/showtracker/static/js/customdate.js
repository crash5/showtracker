export class CustomDate extends Date {
//
    constructor(year, month, day) {
        super();
        this.date = new Date(year, month - 1, day);
    }

    static FromIsoString(string) {
        let res = new CustomDate(1,1,1);
        res.date = new Date(string);
        return res;
    }

    static Now() {
        let res = new CustomDate(1,1,1);
        res.date = new Date();
        return res;
    }

//
    isToday() {
        return this.isSameDate(new Date());
    }

    isWeekend() {
        return this.date.getDay() % 6 == 0;
    }

    isSameDate(otherDate) {
        const date = this.date;
        return (date.getFullYear() == otherDate.getFullYear()
            && date.getMonth() == otherDate.getMonth()
            && date.getDate() == otherDate.getDate());
    }

    isOlderThan(otherDate) {
        const date = this.date;
        return (
            date.getFullYear() < otherDate.getFullYear()
            || (date.getFullYear() == otherDate.getFullYear() && date.getMonth() < otherDate.getMonth())
            || (date.getFullYear() == otherDate.getFullYear() && date.getMonth() == otherDate.getMonth() && date.getDate() < otherDate.getDate())
        );
        // return this.date < otherDate.date;
    }

//
    paddedDay() {
        return this.date.getDate().toString().padStart(2, '0');
    }

    dateFormat() {
        const date = this.date;
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        return `${date.getFullYear()}-${month}-${day}`;
    }

    timeFormat() {
        const hour = this.date.getHours().toString().padStart(2, '0');
        const minute = this.date.getMinutes().toString().padStart(2, '0');
        return `${hour}:${minute}`;
    }

    dateTimeFormat() {
        return `${this.dateFormat()} ${this.timeFormat()}`;
    }

//
    *surroundingDaysIterator(days = 15) {
        let firstDate = new Date(this.date);
        firstDate.setDate(firstDate.getDate() - days)
        let lastDate = new Date(this.date);
        lastDate.setDate(lastDate.getDate() + days);
        for (let date = firstDate; date <= lastDate; date.setDate(date.getDate() + 1)) {
            yield new CustomDate(date.getFullYear(), date.getMonth() + 1, date.getDate());
        }
    }

    *fullMonthIterator() {
        const year = this.date.getFullYear();
        const month = this.date.getMonth() + 1;
        const daysInMonth = new Date(year, month, 0).getDate();
        for (let day = 1; day <= daysInMonth; day++) {
            yield new CustomDate(year, month, day);
        }
    }

    static *dateIterator(first_date, last_date) {
        let firstDate = new Date(first_date);
        let lastDate = new Date(last_date);
        for (let date = firstDate; date <= lastDate; date.setDate(date.getDate() + 1)) {
            yield new CustomDate(date.getFullYear(), date.getMonth() + 1, date.getDate());
        }
    }
};