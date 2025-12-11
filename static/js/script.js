// Seleciona TODOS os botões de curtir
const likeButtons = document.querySelectorAll(".like-btn");

likeButtons.forEach(btn => {
    // Inicializa o estado 'curtido' e a contagem para ESTE botão
    let liked = false; 
    let count = 0; 
    const contador = btn.querySelector(".like-count");
    
    btn.addEventListener("click", () => {
        liked = !liked;
        
        if (liked) {
            count++;
            // Atualiza o HTML usando o 'count' atualizado
            btn.innerHTML = "💖 Descurtir <span class='like-count'>" + count + "</span>";
        } else {
            if (count > 0) {
                count--;
            }
            // Atualiza o HTML usando o 'count' atualizado
            btn.innerHTML = "🤍 Curtir <span class='like-count'>" + count + "</span>";
        }
    });
});

function toggleComentarios(id) {
    const box = document.getElementById("comentarios-" + id);
    box.style.display = (box.style.display === "none") ? "block" : "none";
}





