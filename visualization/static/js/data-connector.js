"use strict";

class DataConnector {
    constructor(plan, callback) {
        this.plan = plan;
        this.stateIndex = 0;
    }

    static loadPlans() {
    }

    nextState() {
    }


    prevState() {
    }
}

class StreamingDataConnector extends DataConnector {
    constructor(plan, callback) {
        super(plan);

        this.simulatorFinished = false;

        // First time loading
        this.loadStreamingData(plan).then(data => {
            this.data = data;
            this.dataSize = data["state"].length;
            callback();
        });
    }

    loadStreamingData(plan, id = -1, steps = 1) {
        return new Promise((res, rej) => {
            $.get(`/data/streaming?plan=${plan}&steps=${steps}&id=${id}`, data => {
                res(JSON.parse(data));
            }).fail(function (jqXHR, textStatus) {
                this.simulatorFinished = true;
                alert(jqXHR.responseText);
            });
        });
    }

    static loadPlans() {
        return new Promise((res, rej) => {
            $.get(`/plans/streaming`, data => {
                res(JSON.parse(data));
            }).fail(function (jqXHR, textStatus) {
                alert(jqXHR.responseText);
            });
        });
    }

    async nextState(stepSize = 1) {
        return new Promise(res => {
            if (this.simulatorFinished || (this.stateIndex + stepSize < this.dataSize)) {
                this.stateIndex = Math.min(this.stateIndex + stepSize, this.dataSize - 1);
                res(this.currentState());
            } else {
                const stepsToSimulate = stepSize - (this.dataSize - 1 - this.stateIndex);
                this.loadStreamingData(this.plan, this.data["simulatorId"], stepsToSimulate).then(state => {
                    if (!state.length) this.simulatorFinished = true;

                    this.data["state"] = this.data["state"].concat(state);
                    this.dataSize = this.data["state"].length;
                    this.stateIndex = this.dataSize - 1;

                    res(this.currentState());
                });
            }
        });
    }

    async prevState(stepSize = 1) {
        this.stateIndex = Math.max(0, this.stateIndex - stepSize);
        return this.currentState();
    }

    currentState() {
        return this.data["state"][this.stateIndex];
    }

    getSurfaceData() {
        if (this.data) {
            return this.data["surface"];
        } else {
            alert("Surface data not ready.");
        }
    }
}

class BatchDataConnector extends DataConnector {
    constructor(plan, callback) {
        super(plan);

        this.loadBatchData(plan).then(data => {
            this.data = data;
            this.dataSize = data["state"].length;
            callback();
        });
    }

    static loadPlans() {
        return new Promise((res, rej) => {
            $.get(`/plans/batch`, data => {
                res(JSON.parse(data));
            }).fail(function (jqXHR, textStatus) {
                alert(jqXHR.responseText);
            });
        });
    }

    loadBatchData(plan) {
        return new Promise((res, rej) => {
            $.get(`/data/batch?plan=${plan}`, data => {
                res(JSON.parse(data));
            }).fail(function (jqXHR, textStatus) {
                alert(jqXHR.responseText);
            });
        });
    }

    async nextState(stepSize = 1) {
        this.stateIndex = (this.stateIndex + stepSize) % this.dataSize;
        return this.currentState();
    }

    async prevState(stepSize = 1) {
        this.stateIndex = (this.stateIndex + this.dataSize - stepSize) % this.dataSize;
        return this.currentState();
    }

    currentState() {
        return this.data["state"][this.stateIndex];
    }

    getSurfaceData() {
        if (this.data) {
            return this.data["surface"];
        } else {
            alert("Surface data not ready.");
        }
    }
}