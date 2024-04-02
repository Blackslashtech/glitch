package main

import (
	"context"
	"fmt"
	"log"

	"github.com/genjidb/genji"
	"github.com/genjidb/genji/types"
	"github.com/titanous/json5"
)

func main() {
	// Create a database instance, here we'll store everything on-disk
	db, err := genji.Open("mydb")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// If needed, attach context, e.g. (*http.Request).Context().
	db = db.WithContext(context.Background())

	// Create a table with a strict schema.
	// Useful to have full control of the table content.
	// Notice that it is possible to define constraint on nested documents.
	err = db.Exec(`
        CREATE TABLE if not exists user (
            id              INT     PRIMARY KEY,
            name            TEXT    NOT NULL UNIQUE,
            friends         ARRAY,
			kek             DOCUMENT
        )
    `)
	if err != nil {
		panic(err)
	}

	err = db.Exec(`CREATE INDEX IF NOT EXISTS idx_user_friends ON user (friends)`)
	if err != nil {
		panic(err)
	}

	// Go structures can be passed directly
	type User struct {
		ID      uint
		Name    string
		Friends []string
		Kek     map[string]any
	}

	goodFriends := []string{"a", "b"}

	// Let's create a user
	u := User{
		ID:      23,
		Name:    "foo3",
		Friends: goodFriends,
		Kek:     map[string]any{"lol\\\": 2.0, kek: 1} // ": 1},
	}
	err = db.Exec(`INSERT INTO user VALUES ?`, &u)
	if err != nil {
		panic(err)
	}

	attackFriends := make([]string, 1000)
	for i := range attackFriends {
		attackFriends[i] = "a"
	}

	// Query some documents
	res, err := db.Query("SELECT * FROM user")
	// always close the result when you're done with it
	defer res.Close()

	res.Iterate(func(d types.Document) error {
		kek, err := d.GetByField("kek")
		fmt.Printf("name=%v, err=%v", kek, err)
		var k any
		if err := json5.Unmarshal([]byte(fmt.Sprintf("%v", kek)), &k); err != nil {
			panic(err)
		}
		fmt.Printf("kek=%v\n", k)
		return nil
	})
}
