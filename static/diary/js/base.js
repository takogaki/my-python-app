document.addEventListener('DOMContentLoaded', function() {
    function updateTime() {
        const now = new Date();

        const year           = now.getFullYear();
        const month          = (now.getMonth() + 1).toString().padStart(2, '0');
        const day            = now.getDate().toString().padStart(2, '0');
        const hours          = now.getHours().toString().padStart(2, '0');
        const minutes        = now.getMinutes().toString().padStart(2, '0');
        const seconds        = now.getSeconds().toString().padStart(2, '0');
        const dateString     = `${year}年${month}月${day}日`;
        const timeString     = `${hours}時${minutes}分${seconds}秒`;
        const dateTimeString = `${dateString} ${timeString}`;
        document.getElementById('clock').textContent = dateTimeString;
    }
    updateTime();
    setInterval(updateTime, 1000);
});