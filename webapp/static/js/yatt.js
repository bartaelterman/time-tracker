/**
* Project
*/
function Project(data) {
    var self = this;
    self.name = ko.observable(data.name);
    self.customer = ko.observable(data.customer);
    self.company = ko.observable(data.company);
    self.team = ko.observable(data.team.name);
    self.hourlyRate = ko.observable(data.hourly_rate);
    self.activities = ko.observableArray(data.activities);
}

function Activity(data) {
    var self = this;
    self.id = ko.observable(data.id);
    self.username = ko.observable(data.username);
    self.start = ko.observable(data.start);
    self.minutes = ko.observable(data.minutes);
    self.duration_str = ko.observable(data.duration_str ? data.duration_str : self.minutes() + " minutes");
    self.description = ko.observable(data.description);
    self.billable = ko.observable(data.billable);
    self.jsonify = function() {
        return ko.toJSON({
            username: self.username(),
	    start: self.start(),
	    minutes: self.minutes(),
	    duration_str: self.duration_str,
	    description: self.description(),
	    billable: self.billable().toString()
	});
    }
}

function ProjectListViewModel() {
    var self = this;
    self.existingProjects = ko.observableArray([]);
    self.selectedProject = ko.observable();
    self.newActivityDate = ko.observable();
    self.newActivityStarttime = ko.observable();
    self.newActivityDuration = ko.observable();
    self.newActivityDescription = ko.observable();
    self.newActivityBillable = ko.observable(false);

    self.getProjects = function() {
        $.getJSON("/projects", function(allData) {
            var mappedProjects = $.map(allData.projects, function(item) {return new Project(item)});
            self.existingProjects(mappedProjects);
            console.log(self.existingProjects())
        });
    }

    self.addActivity = function() {
        var activity = new Activity({
            username: 'bartaelterman',
	    start: self.newActivityDate() + " " + self.newActivityStarttime() + ":00",
	    minutes: self.newActivityDuration(),
	    description: self.newActivityDescription(),
	    billable: self.newActivityBillable()
        });
        console.log(activity.jsonify())
        $.ajax("/projects/" + self.selectedProject().name() + "/activities", {
            data: activity.jsonify(),
            type: "post", contentType: "application/json",
            success: function(result) {
		self.selectedProject().activities.push(activity);
                self.newActivityDate("");
                self.newActivityStarttime("");
                self.newActivityDuration("");
                self.newActivityDescription("");
                self.newActivityBillable("");
            }
        });
    }

    self.deleteActivity = function(activity) {
        $.ajax("/projects/" + self.selectedProject().name() + "/activities/" + activity.id, {
            type: "delete",
            success: function(result) {
                self.selectedProject().activities.remove(activity);
                console.log(result);
            }
        });
    }

    self.getProjects();
}

function User(data) {
    var self = this;
    self.username = ko.observable(data.username);
    self.email = ko.observable(data.email);
    self.createdAt = ko.observable(data.created_at);
}

function UserListViewModel() {
    var self = this;
    self.users = ko.observableArray([]);

    self.newUsername = ko.observable(); // for binding the form to new user data
    self.newUserEmail = ko.observable(); // for binding the form to new user data

    self.getUsers = function() {
        $.getJSON("/users", function(allData) {
//            console.log(allData);
            var mappedUsers = $.map(allData.users, function(item) {return new User(item)});
            self.users(mappedUsers);
//            console.log(self.users());
        });
    }

    self.createUser = function() {
        console.log(ko.toJSON({username: self.newUsername(), email: self.newUserEmail()}));
        $.ajax("/users/", {
            data: ko.toJSON({username: self.newUsername(), email: self.newUserEmail()}),
            type: "post", contentType: "application/json",
            success: function(result) {
                self.newUsername("");
                self.newUserEmail("");
                self.getUsers();
                console.log(result)
            }
        });
    }

    self.deleteUser = function(user) {
        $.ajax("/users/" + user.username(), {
            type: "delete",
            success: function(result) {
                console.log(result);
                self.getUsers();
            }
        });
    }

    self.getUsers();
}

//ko.applyBindings(new UserListViewModel());
