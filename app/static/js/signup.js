const form = $('#form-signup');


$('#btn-submit').click(e => {
    e.preventDefault()
    console.log(form.name)
})

const constraints = {
    name: {
        presence: true,
        message: 'Esse campo é obrigatório',
        format: {
            pattern: /^[a-zA-Z]{4,}(?: [a-zA-Z]+){0,2}$/,
            message: "'%{value}' não é um nome válido"
        }
    }
}