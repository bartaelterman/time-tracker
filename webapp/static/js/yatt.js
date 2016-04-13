function User(data) {
    this.username = ko.observable(data.username);
    this.email = ko.observable(data.email);
    this.createdAt = ko.observable(data.created_at);
}

function UserListViewModel() {
    var self = this;
    self.users = ko.observableArray([]);

    self.newUsername = ko.observable(); // for binding the form to new user data
    self.newUserEmail = ko.observable(); // for binding the form to new user data

    self.getUsers = function() {
        $.getJSON("/users", function(allData) {
            console.log(allData);
            var mappedUsers = $.map(allData.users, function(item) {return new User(item)});
            self.users(mappedUsers);
            console.log(self.users());
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

ko.applyBindings(new UserListViewModel());
