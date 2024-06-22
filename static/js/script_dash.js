function toggleMenu() {
    var sidebar = document.getElementById('sidebar');
    var content = document.getElementById('content');
    var header = document.getElementById('header');
    sidebar.classList.toggle('active');
    if (sidebar.classList.contains('active')) {
      content.style.marginLeft = '250px';
      header.style.left = '250px';
    } else {
      content.style.marginLeft = '0';
      header.style.left = '0';
    }
  }

  // Fungsi untuk mengganti tema
  function toggleTheme() {
    var body = document.body;
    body.classList.toggle('light-theme');
  }

  // Fungsi untuk menampilkan opsi profil
  function toggleProfileOptions() {
    var profileOptions = document.getElementById('profile-options');
    profileOptions.classList.toggle('show');
  }

  // Fungsi untuk mendapatkan total visitor dari server
  function getTotalVisitor() {
    // Ganti URL dengan URL endpoint yang sesuai di server Anda
    fetch('https://ryochi.my.id/getTotalVisitor')
      .then(response => response.json())
      .then(data => {
        // Perbarui nilai total visitor di halaman web
        document.querySelector('.card-content').textContent = data.totalVisitor;
      })
      .catch(error => console.error('Error:', error));
  }

  // Panggil fungsi untuk mendapatkan total visitor saat halaman dimuat
  document.addEventListener('DOMContentLoaded', getTotalVisitor);

  // Fungsi untuk menambah total visitor setiap kali halaman diakses
  function increaseVisitorCount() {
    // Kirim permintaan ke server untuk menambah jumlah total visitor
    fetch('https://ryochi.my.id/increaseVisitorCount', { method: 'POST' })
      .then(response => {
        if (response.ok) {
          // Jika permintaan berhasil, panggil kembali fungsi untuk mendapatkan total visitor
          getTotalVisitor();
        } else {
          console.error('Error:', response.statusText);
        }
      })
      .catch(error => console.error('Error:', error));
  }

  // Panggil fungsi untuk menambah total visitor saat halaman dimuat
  increaseVisitorCount();