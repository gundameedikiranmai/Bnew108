db.getSiblingDB('admin').auth(
    "rasa_admin",
    "rasa_admin"
);
db.createUser({
    user: "rasa",
    pwd: "rasa",
    roles: ["readWrite"],
});