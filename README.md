Quick and dirty demo

Some things to be aware of:

    Not all functionality is present. Missing S3, for example.

    Models could be different. (Breaking out separate authors table etc.)

    Validation could be more involved. Break things out and validate 'row' and all incoming data. Do more checks etc.

    More tests. Along with some additional integration/functional tests.

    Could have better project structure.

    Models could have tighter contraints for integrity and obviously, use Postgres and not sqlite in production. :)