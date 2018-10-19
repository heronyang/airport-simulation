"use strict";

class DataConnector {
    constructor(plan, callback) {
        this.plan = plan;
        this.state_index = 0;
    }

    nextState() {
    }


    prevState() {
    }
}

class StreamingDataConnector extends DataConnector {

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

    loadBatchData(plan) {
        return new Promise((res, rej) => {
            $.get(`/expr_data?plan=${plan}`, data => {
                res(JSON.parse(data));
            }).fail(function (jqXHR, textStatus) {
                alert(jqXHR.responseText);
            });
        });

    }

    nextState(stepSize = 1) {
        this.state_index = (this.state_index + stepSize) % this.dataSize;
        return this.currentState();
    }

    prevState(stepSize = 1) {
        this.state_index = (this.state_index + this.dataSize - stepSize) % this.dataSize;
        return this.currentState();
    }

    currentState() {
        return this.data["state"][this.state_index];
    }

    getSurfaceData() {
        if (this.data) {
            return this.data["surface"];
        } else {
            alert("Surface data not ready.");
        }
    }
}